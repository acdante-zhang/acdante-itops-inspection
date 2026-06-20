package api

import (
	"net/http"
	"strconv"
	"time"

	"acdante-sqlmon/models"
	"acdante-sqlmon/services"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	r := gin.Default()

	r.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:5000", "http://127.0.0.1:5000"},
		AllowMethods:     []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Authorization"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	v1 := r.Group("/api/v1")

	// Health
	v1.GET("/health", healthCheck)

	// Dashboard
	v1.GET("/dashboard/stats", getDashboardStats)

	// Targets (巡检对象)
	v1.GET("/targets", getTargets)
	v1.GET("/targets/:id", getTarget)
	v1.POST("/targets", createTarget)
	v1.PUT("/targets/:id", updateTarget)
	v1.DELETE("/targets/:id", deleteTarget)
	v1.POST("/targets/:id/test", testTargetConnection)

	// Templates (巡检模板)
	v1.GET("/templates", getTemplates)
	v1.GET("/templates/:id", getTemplate)
	v1.POST("/templates", createTemplate)
	v1.PUT("/templates/:id", updateTemplate)
	v1.DELETE("/templates/:id", deleteTemplate)

	// Tasks (巡检任务)
	v1.GET("/tasks", getTasks)
	v1.GET("/tasks/:id", getTask)
	v1.POST("/tasks", createTask)
	v1.PUT("/tasks/:id", updateTask)
	v1.DELETE("/tasks/:id", deleteTask)
	v1.POST("/tasks/:id/run", runTask)

	// Results (巡检结果)
	v1.GET("/results", getResults)

	// Reports (巡检报告)
	v1.GET("/reports", getReports)
	v1.GET("/reports/:id", getReport)
	v1.POST("/reports/generate", generateReport)
	v1.GET("/reports/:id/download", downloadReport)

	// Knowledge (巡检知识库)
	v1.GET("/knowledge", getKnowledge)
	v1.GET("/knowledge/:id", getKnowledgeDetail)

	return r
}

// --- Health ---

func healthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "healthy",
		"service":   "Acdante ITOps Inspection Platform",
		"version":   "1.0.0",
		"timestamp": time.Now().UTC(),
	})
}

// --- Dashboard ---

func getDashboardStats(c *gin.Context) {
	c.JSON(http.StatusOK, services.GetDashboardStats())
}

// --- Targets ---

func getTargets(c *gin.Context) {
	targetType := c.Query("type")
	if targetType != "" {
		c.JSON(http.StatusOK, gin.H{"targets": services.GetTargetsByType(models.TargetType(targetType))})
		return
	}
	c.JSON(http.StatusOK, gin.H{"targets": services.GetTargets()})
}

func getTarget(c *gin.Context) {
	id := c.Param("id")
	var targetID int
	if _, err := parseID(id, &targetID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的ID"})
		return
	}
	t := services.GetTarget(targetID)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "巡检对象不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func createTarget(c *gin.Context) {
	var req models.InspectionTarget
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.AddTarget(req)
	c.JSON(http.StatusCreated, t)
}

func updateTarget(c *gin.Context) {
	id := c.Param("id")
	var targetID int
	if _, err := parseID(id, &targetID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的ID"})
		return
	}
	var req models.InspectionTarget
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.UpdateTarget(targetID, req)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "巡检对象不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func deleteTarget(c *gin.Context) {
	id := c.Param("id")
	var targetID int
	if _, err := parseID(id, &targetID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的ID"})
		return
	}
	services.DeleteTarget(targetID)
	c.JSON(http.StatusOK, gin.H{"message": "已删除"})
}

func testTargetConnection(c *gin.Context) {
	id := c.Param("id")
	var targetID int
	if _, err := parseID(id, &targetID); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "无效的ID"})
		return
	}
	result := services.TestTargetConnection(targetID)
	c.JSON(http.StatusOK, result)
}

// --- Templates ---

func getTemplates(c *gin.Context) {
	targetType := c.Query("type")
	if targetType != "" {
		c.JSON(http.StatusOK, gin.H{"templates": services.GetTemplatesByType(models.TargetType(targetType))})
		return
	}
	c.JSON(http.StatusOK, gin.H{"templates": services.GetTemplates()})
}

func getTemplate(c *gin.Context) {
	id := c.Param("id")
	t := services.GetTemplate(id)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "模板不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func createTemplate(c *gin.Context) {
	var req models.InspectionTemplate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.AddTemplate(req)
	c.JSON(http.StatusCreated, t)
}

func updateTemplate(c *gin.Context) {
	id := c.Param("id")
	var req models.InspectionTemplate
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.UpdateTemplate(id, req)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "模板不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func deleteTemplate(c *gin.Context) {
	id := c.Param("id")
	services.DeleteTemplate(id)
	c.JSON(http.StatusOK, gin.H{"message": "已删除"})
}

// --- Tasks ---

func getTasks(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"tasks": services.GetTasks()})
}

func getTask(c *gin.Context) {
	id := c.Param("id")
	t := services.GetTask(id)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "任务不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func createTask(c *gin.Context) {
	var req models.InspectionTask
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.AddTask(req)
	c.JSON(http.StatusCreated, t)
}

func updateTask(c *gin.Context) {
	id := c.Param("id")
	var req models.InspectionTask
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	t := services.UpdateTask(id, req)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "任务不存在"})
		return
	}
	c.JSON(http.StatusOK, t)
}

func deleteTask(c *gin.Context) {
	id := c.Param("id")
	services.DeleteTask(id)
	c.JSON(http.StatusOK, gin.H{"message": "已删除"})
}

func runTask(c *gin.Context) {
	id := c.Param("id")
	t := services.RunTask(id)
	if t == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "任务不存在"})
		return
	}
	c.JSON(http.StatusOK, gin.H{"task": t, "message": "任务已触发执行"})
}

// --- Results ---

func getResults(c *gin.Context) {
	taskID := c.Query("task_id")
	targetID := 0
	if tid := c.Query("target_id"); tid != "" {
		if _, err := parseID(tid, &targetID); err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "无效的target_id"})
			return
		}
	}
	c.JSON(http.StatusOK, gin.H{"results": services.GetResults(taskID, targetID)})
}

// --- Reports ---

func getReports(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"reports": services.GetReports()})
}

func getReport(c *gin.Context) {
	id := c.Param("id")
	r := services.GetReport(id)
	if r == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "报告不存在"})
		return
	}
	c.JSON(http.StatusOK, r)
}

func generateReport(c *gin.Context) {
	var req struct {
		TaskID string              `json:"task_id" binding:"required"`
		Format models.ReportFormat `json:"format"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if req.Format == "" {
		req.Format = models.ReportHTML
	}
	r := services.GenerateReport(req.TaskID, req.Format)
	if r == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "任务不存在或无结果数据"})
		return
	}
	c.JSON(http.StatusCreated, r)
}

func downloadReport(c *gin.Context) {
	id := c.Param("id")
	format := c.DefaultQuery("format", "html")
	r := services.GetReport(id)
	if r == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "报告不存在"})
		return
	}
	// Generate a simple HTML report for download
	html := generateHTMLReport(r)
	c.Header("Content-Type", "text/html; charset=utf-8")
	c.Header("Content-Disposition", "attachment; filename="+id+".html")
	c.String(http.StatusOK, html)
}

func generateHTMLReport(r *models.InspectionReport) string {
	html := `<!DOCTYPE html><html><head><meta charset="utf-8"><title>` + r.TaskName + `</title>
<style>
body{font-family:Arial,sans-serif;margin:40px;color:#333}
.header{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;padding:30px;border-radius:8px;margin-bottom:20px}
.header h1{margin:0;font-size:24px}.header p{margin:5px 0 0;opacity:0.8}
.stats{display:flex;gap:16px;margin:20px 0}
.stat{flex:1;padding:16px;border-radius:8px;text-align:center}
.stat-ok{background:#dcfce7;color:#166534}
.stat-warn{background:#fef3c7;color:#92400e}
.stat-crit{background:#fecaca;color:#991b1b}
.stat h3{margin:0;font-size:28px}.stat p{margin:4px 0 0}
table{width:100%;border-collapse:collapse;margin:16px 0}
th,td{border:1px solid #e2e8f0;padding:8px 12px;text-align:left;font-size:14px}
th{background:#f8fafc;font-weight:600}
.critical{color:#dc2626;font-weight:700}
.warning{color:#d97706;font-weight:700}
.ok{color:#16a34a}
.issue{background:#fff5f5;border-left:4px solid #dc2626;padding:12px;margin:8px 0;border-radius:4px}
.footer{margin-top:30px;padding-top:16px;border-top:1px solid #e2e8f0;font-size:12px;color:#94a3b8;text-align:center}
</style></head><body>
<div class="header"><h1>` + r.TaskName + `</h1><p>Acdante ITOps Inspection Platform | 生成时间: ` + r.GeneratedAt.Format("2006-01-02 15:04:05") + `</p></div>
<div class="stats">
<div class="stat stat-ok"><h3>` + intToStr(r.OKCount) + `</h3><p>正常</p></div>
<div class="stat stat-warn"><h3>` + intToStr(r.WarningCount) + `</h3><p>警告</p></div>
<div class="stat stat-crit"><h3>` + intToStr(r.CriticalCount) + `</h3><p>严重</p></div>
<div class="stat" style="background:#f0f9ff;color:#075985"><h3>` + intToStr(r.HealthScore) + `</h3><p>健康度</p></div>
</div>
<h2>问题列表</h2>`
	if len(r.Issues) == 0 {
		html += `<p style="color:#16a34a">未发现问题</p>`
	} else {
		html += `<table><tr><th>巡检对象</th><th>巡检项</th><th>分类</th><th>状态</th><th>当前值</th><th>阈值</th><th>建议</th></tr>`
		for _, issue := range r.Issues {
			cls := "warning"
			if issue.Status == models.ResultCritical {
				cls = "critical"
			}
			html += `<tr><td>` + issue.TargetName + `</td><td>` + issue.ItemName + `</td><td>` + issue.Category + `</td><td class="` + cls + `">` + string(issue.Status) + `</td><td>` + issue.Value + `</td><td>` + issue.Threshold + `</td><td>` + issue.Suggestion + `</td></tr>`
		}
		html += `</table>`
	}
	html += `<h2>详细结果</h2><table><tr><th>巡检对象</th><th>巡检项</th><th>分类</th><th>状态</th><th>原始值</th><th>耗时(ms)</th></tr>`
	for _, res := range r.Results {
		cls := "ok"
		if res.Status == models.ResultCritical {
			cls = "critical"
		} else if res.Status == models.ResultWarning {
			cls = "warning"
		}
		html += `<tr><td>` + res.TargetName + `</td><td>` + res.ItemName + `</td><td>` + res.Category + `</td><td class="` + cls + `">` + string(res.Status) + `</td><td>` + res.RawValue + `</td><td>` + intToStr(res.DurationMs) + `</td></tr>`
	}
	html += `</table><div class="footer">Acdante ITOps Inspection Platform v1.0.0 | Powered by Acdante AI</div></body></html>`
	return html
}

// --- Knowledge ---

func getKnowledge(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"entries": services.GetKnowledgeEntries()})
}

func getKnowledgeDetail(c *gin.Context) {
	id := c.Param("id")
	e := services.GetKnowledgeEntry(id)
	if e == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "知识条目不存在"})
		return
	}
	c.JSON(http.StatusOK, e)
}

// --- Helpers ---

func parseID(s string, out *int) (bool, error) {
	var err error
	*out, err = strconv.Atoi(s)
	return err == nil, err
}

func intToStr(i int) string {
	return strconv.Itoa(i)
}
