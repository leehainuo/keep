package v1
import (
	"github.com/gin-gonic/gin"

	"keep-api/internal/handler/ping"
	"keep-api/internal/svc"
)

// RegisterV1 - Register v1 routes
func RegisterV1(r *gin.Engine, svc *svc.ServiceContext) {
	// Health check
	r.GET("/ping", ping.PingHandler(svc))

	// API v1 route group
	// v1 := r.Group("/api/v1")
	// {

	// }
}
