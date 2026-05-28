package config

import (
	"fmt"

	"keep-api/pkg/logn"
	"keep-api/pkg/stores/redis"
	"keep-api/pkg/stores/sqlx"

	"github.com/spf13/viper"
)

// Config - Configuration
type Config struct {
	App    AppConf         `mapstructure:"keep"`
	Server ServerConf      `mapstructure:"server"`
	MySQL  sqlx.MySQLConf  `mapstructure:"mysql"`
	Redis  redis.RedisConf `mapstructure:"redis"`
	Log    logn.LogConf    `mapstructure:"log"`
}

// AppConf - Application configuration
type AppConf struct {
	Name string `mapstructure:"name"`
	Env  string `mapstructure:"env"`
}

// ServerConf - Server configuration
type ServerConf struct {
	Host         string `mapstructure:"host"`
	Port         int    `mapstructure:"port"`
	ReadTimeout  int    `mapstructure:"read_timeout"`
	WriteTimeout int    `mapstructure:"write_timeout"`
}

// ConfigType - Configuration file type
const ConfigType = "yaml"

// Init - Initialize configuration
func Init(path string) (*Config, error) {
	v := viper.New()
	v.SetConfigFile(path)
	v.SetConfigType(ConfigType)

	// Read config file - Option
	if err := v.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	// Enable environment variable override
	v.AutomaticEnv()

	// Unmarshal config
	c := &Config{}
	if err := v.Unmarshal(c); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return c, nil
}
