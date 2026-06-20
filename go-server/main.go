package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"sync"

	"acdante-sqlmon/api"
)

func main() {
	port := "8080"

	// 启动 Rust 数据引擎
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		startRustEngine()
	}()

	// 启动 Go API 网关
	router := api.SetupRouter()
	addr := fmt.Sprintf("0.0.0.0:%s", port)
	log.Printf("[AcdanteSQLMon] Go API 网关启动于 %s", addr)
	log.Printf("[AcdanteSQLMon] Rust 数据引擎启动于 0.0.0.0:8081")

	if err := router.Run(addr); err != nil {
		log.Fatalf("Go 服务启动失败: %v", err)
	}
}

// startRustEngine 启动 Rust 数据引擎
func startRustEngine() {
	rustBin := "/workspace/projects/rust-engine/target/release/acdante-sqlmon-engine"
	if _, err := os.Stat(rustBin); err != nil {
		rustBin = "/workspace/projects/rust-engine/target/debug/acdante-sqlmon-engine"
		if _, err := os.Stat(rustBin); err != nil {
			log.Printf("[Rust Engine] 未找到编译产物，降级为 Go 本地分析模式")
			return
		}
	}

	cmd := exec.Command(rustBin)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	log.Printf("[Rust Engine] 启动 Rust 数据引擎: %s", rustBin)
	if err := cmd.Run(); err != nil {
		log.Printf("[Rust Engine] Rust 数据引擎异常退出: %v", err)
	}
}
