package api

import (
	"net/http"
	"time"

	"acdante-sqlmon/services"

	"github.com/gin-gonic/gin"
)

// RustBridge 代理请求到 Rust 数据引擎
func RustBridge(target string) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 简化: 直接使用 Go 本地数据，Rust 引擎可用时代理
		c.Next()
	}
}

// ProxyToRust 代理分析请求到 Rust 引擎
func ProxyToRust(c *gin.Context) {
	// 尝试代理到 Rust 引擎
	url := "http://localhost:8081" + c.Request.URL.Path

	// 简化实现: 如果 Rust 引擎不可用，使用 Go 本地分析
	resp, err := http.Get(url)
	if err != nil {
		// Rust 不可用，使用本地实现
		instanceID := c.Param("instance_id")
		analysis := services.GenerateAnalysis(instanceID)
		c.JSON(http.StatusOK, analysis)
		return
	}
	defer resp.Body.Close()

	// 转发 Rust 响应
	c.DataFromReader(resp.StatusCode, resp.ContentLength, resp.Header.Get("Content-Type"), resp.Body, nil)
}

// 分析相关的端点
func SetupAnalysisRoutes(r *gin.Engine) {
	r.GET("/api/v1/analysis/:instance_id", ProxyToRust)
}

func init() {
	// 注册分析路由在 SetupRouter 之外
}

// healthCheckWithRust 带有 Rust 引擎状态的健康检查
func HealthCheckWithRust(c *gin.Context) {
	rustStatus := "unavailable"
	client := &http.Client{Timeout: 2 * time.Second}
	resp, err := client.Get("http://localhost:8081/health")
	if err == nil && resp.StatusCode == 200 {
		rustStatus = "running"
		resp.Body.Close()
	}

	c.JSON(http.StatusOK, gin.H{
		"status":       "healthy",
		"service":      "AcdanteSQLMon API Gateway",
		"rust_engine":  rustStatus,
		"timestamp":    time.Now().UTC(),
	})
}
