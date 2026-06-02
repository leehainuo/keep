# Deploy

本目录存放本地开发和演示环境所需的部署资产，和应用代码解耦。
运行期数据统一挂载到项目根目录的 `../.data/`，配置文件仍留在 `deploy/` 下。

## 目录

- `docker-compose.yaml`: 基础依赖容器编排
- `prometheus/`: Prometheus 配置
- `grafana/`: Grafana 数据源和看板目录

## 挂载策略

- 配置文件: `deploy/` 下 bind mount
- 运行数据: 项目根目录 `.data/`
- Git 忽略: 根目录 `.gitignore` 已忽略 `.data/`

## 启动

```bash
cd /Users/lihainuo/Develop/Code/Pers/keep/deploy
docker compose up -d
docker compose ps
```

首次启动后，Docker 会自动创建以下本地目录：

- `../.data/redis`
- `../.data/elasticsearch`
- `../.data/mysql`
- `../.data/prometheus`
- `../.data/grafana`

## 端口

- Redis: `6379`
- Elasticsearch: `9200`
- MySQL: `3306`
- Prometheus: `9090`
- Jaeger: `16686`
- OTLP gRPC: `4317`
- OTLP HTTP: `4318`
- Grafana: `3000`

## keep-ai 环境变量建议

`/Users/lihainuo/Develop/Code/Pers/keep/keep-ai/.env`

```env
ES_URL=http://localhost:9200
ES_USERNAME=
ES_PASSWORD=
PROMETHEUS_URL=http://localhost:9090
JAEGER_URL=http://localhost:16686
OTLP_HTTP_ENDPOINT=http://localhost:4318
REDIS_ADDR=localhost:6379
```
