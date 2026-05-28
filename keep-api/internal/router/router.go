package router

import (
	"github.com/gin-gonic/gin"

	"keep-api/internal/router/v1"
	"keep-api/internal/svc"
)

// Setup - Setup router
func Setup(svc *svc.ServiceContext) *gin.Engine {
	r := gin.New()

	// Global middleware (order matters)
	r.Use(gin.Recovery())               // 1. Recover from panics
	r.Use(gin.Logger())                 // 2. Request logging

	// Register route groups
	v1.RegisterV1(r, svc)

	return r
}
