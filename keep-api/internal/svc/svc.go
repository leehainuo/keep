package svc

import (
	"keep-api/config"
	"keep-api/pkg/stores/redis"
	"keep-api/pkg/stores/sqlx"
)

// ServiceContext - Service context with all dependencies
// Note: No DB field - following go-zero's design philosophy
type ServiceContext struct {
	Config *config.Config
	Redis  *redis.Client

	// Models
}

func NewServiceContext(c *config.Config) (*ServiceContext, error) {
	// Init database connection via sqlconn (go-zero compatible)
	_, err := sqlx.NewMysql(
		c.MySQL.DSN(),
		sqlx.WithMaxOpenConns(c.MySQL.MaxOpenConns),
		sqlx.WithMaxIdleConns(c.MySQL.MaxIdleConns),
		sqlx.WithConnMaxLifetime(c.MySQL.ConnMaxLifetime),
	)
	if err != nil {
		return nil, err
	}

	// Init redis
	rdb, err := redis.Init(c.Redis)
	if err != nil {
		return nil, err
	}

	return &ServiceContext{
		Config: c,
		Redis:  rdb,

		// Init models with SqlConn interface
	}, nil
}
