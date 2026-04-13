# 🌀 Go Vortex — Security Hardening v5.2

> **Moduł:** `vortex/auth.go` | **Warstwa:** Infrastruktura (Go)
> **Port:** 1740
> **Wersja:** v5.2 (2026-04-11)
> **Problem:** Brak autoryzacji na porcie 1740 — bezpośredni dostęp do EBDI state machine

---

## 🎯 Problem (v5.1 i wcześniej)

Go Vortex (port 1740) obsługuje EBDI state machine i oracle digital root — ale był dostępny bez jakiejkolwiek autoryzacji. Bezpośredni dostęp pozwalałby:
- Manipulować wektorem PAD z pominięciem całego kodeksu
- Wymusić dowolny poziom Stress (np. Stress=0 → zerowa czujność)
- Podrabiać wyniki digital root sygnatury 369
- Ominąć PADTherapyDetector (v5.1) przez bezpośredni zapis do state machine

---

## 🏗️ Architektura Bezpieczeństwa (v5.2)

```
Internet / Inne serwisy
          │
          ▼
  ┌───────────────┐
  │   Firewall    │  Port 1740 — TYLKO localhost / sieć wewnętrzna
  │   (iptables)  │  Zablokowany z zewnątrz
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │  mTLS Layer   │  Certyfikat klienta wymagany
  │  (Go TLS)     │  Tylko znane agenty mogą połączyć się
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │  JWT Auth     │  Każde żądanie z podpisanym JWT (HS256)
  │  Middleware   │  Token wydawany przez Sentinela (TTL: 5min)
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │  Rate Limiter │  Max 100 req/min per agent
  │               │  Burst: 10 req/s
  └───────┬───────┘
          │
          ▼
  ┌───────────────┐
  │  EBDI Handler │  Właściwa logika state machine
  └───────────────┘
```

---

## 🐹 Implementacja Go

```go
package vortex

import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "net/http"
    "os"
    "strings"
    "time"
    "sync"

    "github.com/golang-jwt/jwt/v5"
    "golang.org/x/time/rate"
)

// ── Konfiguracja autoryzacji ─────────────────────────────────────────────────

type VortexConfig struct {
    JWTSecret      []byte
    CACertPath     string
    ServerCertPath string
    ServerKeyPath  string
    AllowedAgents  []string    // Lista agentów uprawnionych do Vortex
    RateLimitRPM   int         // Requests per minute per agent
}

var DefaultConfig = VortexConfig{
    AllowedAgents: []string{
        "Orchestrator",
        "Sentinel",
        "Healer",      // Healer potrzebuje EBDI do healing
        // Librarian, SAP, Auditor, Architect NIE mają dostępu do Vortex
    },
    RateLimitRPM: 100,
}

// ── JWT Claims ────────────────────────────────────────────────────────────────

type VortexClaims struct {
    AgentName  string   `json:"agent"`
    AgentID    string   `json:"agent_id"`
    Permissions []string `json:"permissions"`
    jwt.RegisteredClaims
}

// ── Rate Limiter per Agent ────────────────────────────────────────────────────

type AgentRateLimiter struct {
    limiters map[string]*rate.Limiter
    mu       sync.Mutex
    rpm      int
}

func NewAgentRateLimiter(rpm int) *AgentRateLimiter {
    return &AgentRateLimiter{
        limiters: make(map[string]*rate.Limiter),
        rpm:      rpm,
    }
}

func (a *AgentRateLimiter) Allow(agentName string) bool {
    a.mu.Lock()
    defer a.mu.Unlock()
    if _, ok := a.limiters[agentName]; !ok {
        // rate.Every(time.Minute) / rpm = czas między requestami
        a.limiters[agentName] = rate.NewLimiter(
            rate.Every(time.Minute/time.Duration(a.rpm)),
            10, // burst
        )
    }
    return a.limiters[agentName].Allow()
}

// ── Middleware Stack ──────────────────────────────────────────────────────────

type VortexServer struct {
    config      VortexConfig
    rateLimiter *AgentRateLimiter
    mux         *http.ServeMux
}

func NewVortexServer(cfg VortexConfig) *VortexServer {
    s := &VortexServer{
        config:      cfg,
        rateLimiter: NewAgentRateLimiter(cfg.RateLimitRPM),
        mux:         http.NewServeMux(),
    }
    s.registerRoutes()
    return s
}

func (s *VortexServer) registerRoutes() {
    // Każda trasa owinięta w stack middleware
    s.mux.HandleFunc("/ebdi/state",    s.chain(s.handleEBDIState))
    s.mux.HandleFunc("/ebdi/update",   s.chain(s.handleEBDIUpdate))
    s.mux.HandleFunc("/oracle/root",   s.chain(s.handleDigitalRoot))
    s.mux.HandleFunc("/health",        s.handleHealth)   // Bez auth — health check
}

// chain aplikuje middleware: rate limit → JWT auth → handler
func (s *VortexServer) chain(next http.HandlerFunc) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        // 1. Rate limiting
        agentName := r.Header.Get("X-Agent-Name")
        if !s.rateLimiter.Allow(agentName) {
            http.Error(w, `{"error":"rate_limit_exceeded"}`, http.StatusTooManyRequests)
            return
        }

        // 2. JWT autentykacja
        claims, err := s.validateJWT(r)
        if err != nil {
            genesisRecord.LogEvent("VORTEX_AUTH_FAILURE", map[string]any{
                "agent":  agentName,
                "reason": err.Error(),
                "path":   r.URL.Path,
            })
            http.Error(w, `{"error":"unauthorized"}`, http.StatusUnauthorized)
            return
        }

        // 3. Weryfikacja czy agent jest na liście dozwolonych
        if !s.isAllowedAgent(claims.AgentName) {
            http.Error(w,
                fmt.Sprintf(`{"error":"agent %s not permitted to access Vortex"}`, claims.AgentName),
                http.StatusForbidden,
            )
            return
        }

        // Dodaj claims do kontekstu i wywołaj właściwy handler
        r = r.WithContext(contextWithClaims(r.Context(), claims))
        next(w, r)
    }
}

func (s *VortexServer) validateJWT(r *http.Request) (*VortexClaims, error) {
    authHeader := r.Header.Get("Authorization")
    if !strings.HasPrefix(authHeader, "Bearer ") {
        return nil, fmt.Errorf("missing Bearer token")
    }
    tokenStr := strings.TrimPrefix(authHeader, "Bearer ")

    token, err := jwt.ParseWithClaims(tokenStr, &VortexClaims{},
        func(t *jwt.Token) (interface{}, error) {
            if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
                return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
            }
            return s.config.JWTSecret, nil
        },
        jwt.WithExpirationRequired(),
        jwt.WithIssuedAt(),
    )
    if err != nil || !token.Valid {
        return nil, fmt.Errorf("invalid token: %w", err)
    }
    return token.Claims.(*VortexClaims), nil
}

func (s *VortexServer) isAllowedAgent(agentName string) bool {
    for _, a := range s.config.AllowedAgents {
        if a == agentName {
            return true
        }
    }
    return false
}

// ── Start z mTLS ──────────────────────────────────────────────────────────────

func (s *VortexServer) ListenAndServeTLS() error {
    // Załaduj CA cert dla weryfikacji klienta (mTLS)
    caCert, err := os.ReadFile(s.config.CACertPath)
    if err != nil {
        return fmt.Errorf("load CA cert: %w", err)
    }
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        ClientAuth: tls.RequireAndVerifyClientCert,  // mTLS — wymagaj certyfikatu klienta
        ClientCAs:  caCertPool,
        MinVersion: tls.VersionTLS13,                // Minimum TLS 1.3
    }

    server := &http.Server{
        Addr:      ":1740",
        Handler:   s.mux,
        TLSConfig: tlsConfig,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    return server.ListenAndServeTLS(s.config.ServerCertPath, s.config.ServerKeyPath)
}

// ── Health check (bez auth) ───────────────────────────────────────────────────

func (s *VortexServer) handleHealth(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"status":"healthy","service":"go-vortex","version":"5.2"}`))
}
```

---

## 🔧 Konfiguracja Sieci (docker-compose.yml fragment)

```yaml
services:
  go-vortex:
    ports:
      # [v5.2] Usuń publiczne mapowanie portu — tylko sieć wewnętrzna
      # PRZED (v5.1 — NIEBEZPIECZNE):
      # - "1740:1740"
      #
      # PO (v5.2 — BEZPIECZNE):
      - "127.0.0.1:1740:1740"   # Tylko localhost
    networks:
      - adrion_internal          # Tylko sieć wewnętrzna Docker
    environment:
      - VORTEX_JWT_SECRET_FILE=/run/secrets/vortex_jwt_secret
      - VORTEX_CA_CERT=/etc/adrion/certs/ca.pem
    secrets:
      - vortex_jwt_secret

  # Tylko serwisy w tej sieci mogą rozmawiać z Vortex
networks:
  adrion_internal:
    internal: true              # Brak dostępu z zewnątrz Docker network
```

---

## 🔒 Reguły Firewall (iptables)

```bash
#!/bin/bash
# Zastosuj po starcie systemu

# Zablokuj port 1740 z zewnątrz
iptables -A INPUT -p tcp --dport 1740 ! -s 127.0.0.0/8 -j DROP

# Dozwól tylko z wewnętrznej sieci Docker (172.16.0.0/12)
iptables -A INPUT -p tcp --dport 1740 -s 172.16.0.0/12 -j ACCEPT
iptables -A INPUT -p tcp --dport 1740 -s 127.0.0.0/8 -j ACCEPT
```

---

## 📋 Changelog

| Wersja | Data | Zmiana |
|--------|------|--------|
| v5.2 | 2026-04-11 | Nowy moduł auth — JWT (TTL 5min) + mTLS + Rate Limiter per agent; izolacja sieciowa (localhost only); lista dozwolonych agentów; docker-compose hardening; iptables rules |
