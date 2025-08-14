import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import re
import threading
import traceback
import os
import json
from pathlib import Path

import doubao

CONFIG_FILE = "doubao_gui_config.json"

def load_config():
    """加载配置文件"""
    default_config = {
        "api_path": "/erp/opentrade/v2/list/trades",
        "model": "doubao-seed-1-6-250615",
        "api_key": "",  # 用户必须自己配置API密钥
        "test_data_file": "MS_25_Environments_variables.json"
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置和保存的配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        else:
            return default_config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        return default_config

def save_config(config):
    """保存配置文件"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存配置文件失败: {e}")


def parse_script_block(script_block: str) -> dict:
    """从 generate_scripts_for_case 的文本块中解析出 case_name、pre1、pre2、body。"""
    result = {"case_name": "", "pre1": "", "pre2": "", "body": ""}

    # 提取用例名
    m = re.search(r"--- 用例: (.*?) ---", script_block)
    if m:
        result["case_name"] = m.group(1).strip()

    # 提取代码块，顺序依次是：可选pre1、pre2、body
    code_blocks = re.findall(r"```(?:beanshell|text)\n(.*?)\n```", script_block, flags=re.DOTALL)
    if len(code_blocks) == 3:
        result["pre1"], result["pre2"], result["body"] = code_blocks
    elif len(code_blocks) == 2:
        # 没有前置脚本1的情况
        result["pre1"] = ""
        result["pre2"], result["body"] = code_blocks
    elif len(code_blocks) == 1:
        result["body"] = code_blocks[0]
    return result


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("用例脚本生成器 (豆包)")
        self.geometry("1400x800")

        self.config = load_config()
        
        self.api_title_var = tk.StringVar(value="接口名称")
        self.case_name_var = tk.StringVar(value="用例名称")
        self.case_count_var = tk.StringVar(value="生成的用例数量: 0")
        self.current_idx_var = tk.IntVar(value=0)
        
        self.api_path_var = tk.StringVar(value=self.config.get("api_path", "/erp/opentrade/v2/list/trades"))
        self.model_var = tk.StringVar(value=self.config.get("model", "doubao-seed-1-6-250615"))
        self.api_key_var = tk.StringVar(value=self.config.get("api_key", ""))
        
        self.test_data_file_var = tk.StringVar(value=self.config.get("test_data_file", "MS_25_Environments_variables.json"))

        self.test_cases = []
        self.script_blocks = []
        self.parsed_cases = []
        self.api_doc = None

        self._bind_config_events()

        self._build_ui()

    def _bind_config_events(self):
        """绑定配置变更事件"""
        # 当配置变量发生变化时自动保存
        self.api_path_var.trace_add("write", self._on_config_change)
        self.model_var.trace_add("write", self._on_config_change)
        self.api_key_var.trace_add("write", self._on_config_change)
        self.test_data_file_var.trace_add("write", self._on_config_change)

    def _on_config_change(self, *args):
        """配置变更时的回调函数"""
        self._save_current_config()

    def _save_current_config(self):
        """保存当前配置"""
        current_config = {
            "api_path": self.api_path_var.get(),
            "model": self.model_var.get(),
            "api_key": self.api_key_var.get(),
            "test_data_file": self.test_data_file_var.get()
        }
        save_config(current_config)

    def _reset_config(self):
        """重置配置到默认值"""
        if messagebox.askyesno("确认重置", "确定要重置所有配置到默认值吗？\n这将清除所有保存的设置。"):
            # 删除配置文件
            try:
                if os.path.exists(CONFIG_FILE):
                    os.remove(CONFIG_FILE)
                    messagebox.showinfo("重置成功", "配置已重置到默认值")
            except Exception as e:
                messagebox.showerror("重置失败", f"删除配置文件失败: {e}")
                return
            
            # 重新加载默认配置
            self.config = load_config()
            
            # 更新UI变量
            self.api_path_var.set(self.config["api_path"])
            self.model_var.set(self.config["model"])
            self.api_key_var.set(self.config["api_key"])
            self.test_data_file_var.set(self.config["test_data_file"])
            
            # 更新文件状态
            self.update_file_status()

    def _build_ui(self) -> None:
        # 顶部：接口输入、生成按钮、数量
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=12, pady=8)

        ttk.Label(top, text="接口").pack(side=tk.LEFT)
        ttk.Entry(top, textvariable=self.api_path_var, width=50).pack(side=tk.LEFT, padx=8)
        self.generate_btn = ttk.Button(top, text="生成", command=self.on_generate)
        self.generate_btn.pack(side=tk.LEFT, padx=8)
        ttk.Label(top, textvariable=self.case_count_var).pack(side=tk.RIGHT)

        # 豆包API配置行
        config_row = ttk.Frame(self)
        config_row.pack(fill=tk.X, padx=12, pady=4)
        
        ttk.Label(config_row, text="模型:").pack(side=tk.LEFT)
        ttk.Entry(config_row, textvariable=self.model_var, width=30).pack(side=tk.LEFT, padx=4)
        
        ttk.Label(config_row, text="API密钥:").pack(side=tk.LEFT, padx=(12, 0))
        ttk.Entry(config_row, textvariable=self.api_key_var, width=50).pack(side=tk.LEFT, padx=4)
        
        # 配置管理按钮
        ttk.Button(config_row, text="重置配置", command=self._reset_config).pack(side=tk.RIGHT, padx=(8, 0))

        # 测试数据文件选择行
        file_row = ttk.Frame(self)
        file_row.pack(fill=tk.X, padx=12, pady=4)
        
        ttk.Label(file_row, text="测试数据:").pack(side=tk.LEFT)
        ttk.Entry(file_row, textvariable=self.test_data_file_var, width=60).pack(side=tk.LEFT, padx=4)
        ttk.Button(file_row, text="选择文件", command=self.select_test_data_file).pack(side=tk.LEFT, padx=4)
        
        # 显示当前选择的文件状态
        self.file_status_var = tk.StringVar(value="")
        ttk.Label(file_row, textvariable=self.file_status_var, foreground="green").pack(side=tk.LEFT, padx=8)

        # 进度与状态
        status_row = ttk.Frame(self)
        status_row.pack(fill=tk.X, padx=12)
        self.status_var = tk.StringVar(value="就绪")
        self.progress = ttk.Progressbar(status_row, mode="indeterminate", length=180)
        self.progress.pack(side=tk.LEFT)
        ttk.Label(status_row, textvariable=self.status_var).pack(side=tk.LEFT, padx=8)

        # 中部：接口名称 + 导航
        mid = ttk.Frame(self)
        mid.pack(fill=tk.X, padx=12, pady=6)
        ttk.Button(mid, text="↑ 上一条", command=self.on_prev).pack(side=tk.LEFT)
        ttk.Entry(mid, textvariable=self.api_title_var, state="readonly", justify=tk.CENTER, width=60).pack(side=tk.LEFT, padx=12, expand=True)
        ttk.Button(mid, text="下一条 ↓", command=self.on_next).pack(side=tk.LEFT)

        # 用例名称行
        case_row = ttk.Frame(self)
        case_row.pack(fill=tk.X, padx=12, pady=4)
        ttk.Label(case_row, text="当前用例:").pack(side=tk.LEFT)
        ttk.Entry(case_row, textvariable=self.case_name_var, state="readonly", justify=tk.CENTER, width=80).pack(side=tk.LEFT, padx=8, expand=True)

        # 四个文本框区域
        body = ttk.Frame(self)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # 第一行：前置脚本1和前置脚本2
        row1 = ttk.Frame(body)
        row1.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        
        # 前置脚本1
        left = ttk.Frame(row1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 6))
        header1 = ttk.Frame(left)
        header1.pack(fill=tk.X)
        ttk.Label(header1, text="前置脚本1").pack(side=tk.LEFT)
        ttk.Button(header1, text="复制", command=lambda: self.copy_text(self.pre1_text)).pack(side=tk.RIGHT)
        self.pre1_text = ScrolledText(left, height=20)
        self.pre1_text.pack(fill=tk.BOTH, expand=True)

        # 前置脚本2
        right = ttk.Frame(row1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(6, 0))
        header2 = ttk.Frame(right)
        header2.pack(fill=tk.X)
        ttk.Label(header2, text="前置脚本2").pack(side=tk.LEFT)
        ttk.Button(header2, text="复制", command=lambda: self.copy_text(self.pre2_text)).pack(side=tk.RIGHT)
        self.pre2_text = ScrolledText(right, height=20)
        self.pre2_text.pack(fill=tk.BOTH, expand=True)

        # 第二行：请求体
        row2 = ttk.Frame(body)
        row2.pack(fill=tk.BOTH, expand=True)
        header3 = ttk.Frame(row2)
        header3.pack(fill=tk.X)
        ttk.Label(header3, text="请求体").pack(side=tk.LEFT)
        ttk.Button(header3, text="复制", command=lambda: self.copy_text(self.body_text)).pack(side=tk.RIGHT)
        self.body_text = ScrolledText(row2, height=20)
        self.body_text.pack(fill=tk.BOTH, expand=True)
        
        # 初始化文件状态
        self.update_file_status()

    def select_test_data_file(self):
        """选择测试数据文件"""
        file_path = filedialog.askopenfilename(
            title="选择测试数据文件",
            filetypes=[
                ("JSON文件", "*.json"),
                ("所有文件", "*.*")
            ],
            initialfile=self.test_data_file_var.get()
        )
        
        if file_path:
            self.test_data_file_var.set(file_path)
            self.update_file_status()
            # 配置会自动保存（通过trace_add事件）

    def update_file_status(self):
        """更新文件状态显示"""
        file_path = self.test_data_file_var.get()
        if not file_path:
            self.file_status_var.set("未选择文件")
            return
            
        if os.path.exists(file_path):
            try:
                # 尝试读取文件内容验证格式
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        self.file_status_var.set(f"✅ 有效文件 ({len(data)} 条数据)")
                    else:
                        self.file_status_var.set("⚠️ 文件格式异常")
            except Exception as e:
                self.file_status_var.set(f"❌ 文件读取失败: {str(e)}")
        else:
            self.file_status_var.set("❌ 文件不存在")

    def copy_text(self, text_widget):
        """复制文本框内容到剪贴板"""
        try:
            content = text_widget.get("1.0", tk.END).strip()
            if content:
                self.clipboard_clear()
                self.clipboard_append(content)
                self.status_var.set("已复制到剪贴板")
            else:
                self.status_var.set("文本框为空，无内容可复制")
        except Exception as e:
            self.status_var.set(f"复制失败: {e}")

    def on_generate(self):
        """生成测试用例"""
        # 验证API密钥
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("错误", "请输入豆包API密钥")
            return
            
        # 验证文件
        file_path = self.test_data_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择有效的测试数据文件")
            return
            
        self.generate_btn.config(state="disabled")
        self.progress.start()
        self.status_var.set("正在生成测试用例...")
        
        # 在新线程中执行生成逻辑
        thread = threading.Thread(target=self._generate_in_thread)
        thread.daemon = True
        thread.start()

    def _generate_in_thread(self):
        """在线程中执行生成逻辑"""
        try:
            # 更新豆包API配置
            doubao.DOUBAO_API_KEY = self.api_key_var.get()
            model = self.model_var.get()
            
            # 获取API文档
            api_path = self.api_path_var.get().strip()
            if not api_path:
                self.status_var.set("请输入接口路径")
                return
            
            self.api_doc = doubao.get_api_doc(api_path)
            if not self.api_doc:
                self.status_var.set("获取API文档失败")
                return
            
            # 设置接口标题
            self.api_title_var.set(api_path)
            
            # 加载测试数据
            env_file_path = self.test_data_file_var.get()
            test_data = doubao.load_test_data(env_file_path)
            
            if test_data == "[]":
                self.status_var.set("测试数据文件为空")
                return
            
            # 设计测试用例
            self.test_cases = doubao.design_knowledge_driven_cases(self.api_doc, test_data, model)
            
            if not self.test_cases:
                self.status_var.set("未能生成测试用例")
                return
            
            # 生成脚本
            self.script_blocks = []
            self.parsed_cases = []
            
            for case in self.test_cases:
                script_block = doubao.generate_scripts_for_case(self.api_doc, case)
                self.script_blocks.append(script_block)
                
                parsed = parse_script_block(script_block)
                self.parsed_cases.append(parsed)
            
            # 更新UI
            self.after(0, self._update_ui_after_generate)
            
        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            print(f"错误详情: {traceback.format_exc()}")
            self.after(0, lambda: self.status_var.set(error_msg))
        finally:
            self.after(0, self._finish_generate)

    def _update_ui_after_generate(self):
        """生成完成后更新UI"""
        self.case_count_var.set(f"生成的用例数量: {len(self.test_cases)}")
        self.current_idx_var.set(0)
        self._display_current_case()
        self.status_var.set(f"成功生成 {len(self.test_cases)} 个测试用例")

    def _finish_generate(self):
        """完成生成操作"""
        self.generate_btn.config(state="normal")
        self.progress.stop()

    def _display_current_case(self):
        """显示当前用例"""
        if not self.parsed_cases:
            return
        
        idx = self.current_idx_var.get()
        if 0 <= idx < len(self.parsed_cases):
            case = self.parsed_cases[idx]
            
            self.case_name_var.set(case["case_name"])
            
            # 清空文本框
            self.pre1_text.delete("1.0", tk.END)
            self.pre2_text.delete("1.0", tk.END)
            self.body_text.delete("1.0", tk.END)
            
            # 填充内容
            if case["pre1"]:
                self.pre1_text.insert("1.0", case["pre1"])
            if case["pre2"]:
                self.pre2_text.insert("1.0", case["pre2"])
            if case["body"]:
                self.body_text.insert("1.0", case["body"])

    def on_prev(self):
        """显示上一条用例"""
        if not self.parsed_cases:
            return
        
        current = self.current_idx_var.get()
        if current > 0:
            self.current_idx_var.set(current - 1)
            self._display_current_case()
            self.status_var.set(f"显示第 {current} 条用例")
        else:
            self.status_var.set("已经是第一条")

    def on_next(self):
        """显示下一条用例"""
        if not self.parsed_cases:
            return
        
        current = self.current_idx_var.get()
        if current < len(self.parsed_cases) - 1:
            self.current_idx_var.set(current + 1)
            self._display_current_case()
            self.status_var.set(f"显示第 {current + 2} 条用例")
        else:
            self.status_var.set("已经是最后一条")


if __name__ == "__main__":
    app = App()
    app.mainloop() 