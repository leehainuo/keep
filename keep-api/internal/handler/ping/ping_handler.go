package ping

import (
	"github.com/gin-gonic/gin"

	"keep-api/internal/logic/ping"
	"keep-api/internal/svc"
	"keep-api/pkg/httpn"
)

func PingHandler(svc *svc.ServiceContext) gin.HandlerFunc {
	return func(c *gin.Context) {
		l := ping.NewPingLogic(c.Request.Context(), svc)
		resp := l.Ping()

		httpn.Ok(c, resp)
	}
}
