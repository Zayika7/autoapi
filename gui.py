#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于Gemini AI的测试用例生成器GUI界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import json
import os
import threading
import traceback

import gemini


class GeminiApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("测试用例生成器 (Gemini)")
        self.geometry("1200x800")

        self.api_path_var = tk.StringVar(value="/api/test/endpoint")
        self.case_count_var = tk.StringVar(value="5")
        self.api_key_var = tk.StringVar(value="")  # 用户必须自己配置API密钥
        self.test_data_file_var = tk.StringVar(value="test_data.json")
        
        self.status_var = tk.StringVar(value="就绪")
        self.progress = None
        
        self.test_cases = []
        self.current_case_index = 0

        self._build_ui()

    def _build_ui(self) -> None:
        config_frame = ttk.LabelFrame(self, text="配置", padding=10)
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(config_frame, text="API路径:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.api_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="用例数量:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Spinbox(config_frame, from_=1, to=20, textvariable=self.case_count_var, width=10).grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(config_frame, text="API密钥:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.api_key_var, width=50, show="*").grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(config_frame, text="测试数据:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(config_frame, textvariable=self.test_data_file_var, width=30).grid(row=1, column=3, padx=5, pady=5)
        ttk.Button(config_frame, text="选择文件", command=self.select_test_data_file).grid(row=1, column=4, padx=5, pady=5)

        ttk.Button(config_frame, text="生成测试用例", command=self.generate_test_cases).grid(row=2, column=1, pady=10)

        status_frame = ttk.Frame(self)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress = ttk.Progressbar(status_frame, mode="indeterminate", length=200)
        self.progress.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT, padx=5)

        case_frame = ttk.LabelFrame(self, text="测试用例", padding=10)
        case_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        nav_frame = ttk.Frame(case_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="← 上一个", command=self.prev_case).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="下一个 →", command=self.next_case).pack(side=tk.LEFT, padx=5)
        
        self.case_info_var = tk.StringVar(value="无测试用例")
        ttk.Label(nav_frame, textvariable=self.case_info_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=20)

        content_frame = ttk.Frame(case_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(content_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        ttk.Label(left_frame, text="用例信息:").pack(anchor=tk.W)
        self.case_info_text = ScrolledText(left_frame, height=15)
        self.case_info_text.pack(fill=tk.BOTH, expand=True)

        # 右侧：测试脚本
        right_frame = ttk.Frame(content_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ttk.Label(right_frame, text="测试脚本:").pack(anchor=tk.W)
        self.script_text = ScrolledText(right_frame, height=15)
        self.script_text.pack(fill=tk.BOTH, expand=True)

        # 底部按钮
        button_frame = ttk.Frame(case_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="复制用例信息", command=lambda: self.copy_text(self.case_info_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="复制测试脚本", command=lambda: self.copy_text(self.script_text)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存所有用例", command=self.save_all_cases).pack(side=tk.RIGHT, padx=5)

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

    def generate_test_cases(self):
        """生成测试用例"""
        # 验证输入
        if not self.api_path_var.get().strip():
            messagebox.showerror("错误", "请输入API路径")
            return
        
        if not self.api_key_var.get().strip():
            messagebox.showerror("错误", "请输入有效的Gemini API密钥")
            return
        
        file_path = self.test_data_file_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showerror("错误", "请选择有效的测试数据文件")
            return

        # 设置API密钥
        gemini.set_gemini_api_key(self.api_key_var.get())
        
        # 开始生成
        self.status_var.set("正在生成测试用例...")
        self.progress.start()
        
        # 在新线程中执行
        thread = threading.Thread(target=self._generate_in_thread)
        thread.daemon = True
        thread.start()

    def _generate_in_thread(self):
        """在线程中生成测试用例"""
        try:
            api_path = self.api_path_var.get().strip()
            env_file_path = self.test_data_file_var.get()
            case_count = int(self.case_count_var.get())
            
            # 调用Gemini模块生成测试用例
            self.test_cases = gemini.generate_test_cases_for_api(api_path, env_file_path, case_count)
            
            if self.test_cases:
                self.after(0, self._on_generation_complete)
            else:
                self.after(0, lambda: self.status_var.set("生成测试用例失败"))
                
        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            print(f"错误详情: {traceback.format_exc()}")
            self.after(0, lambda: self.status_var.set(error_msg))
        finally:
            self.after(0, self._finish_generation)

    def _on_generation_complete(self):
        """生成完成后的处理"""
        self.current_case_index = 0
        self._display_current_case()
        self.status_var.set(f"成功生成 {len(self.test_cases)} 个测试用例")

    def _finish_generation(self):
        """完成生成操作"""
        self.progress.stop()

    def _display_current_case(self):
        """显示当前测试用例"""
        if not self.test_cases:
            return
        
        case = self.test_cases[self.current_case_index]
        
        # 更新导航信息
        self.case_info_var.set(f"用例 {self.current_case_index + 1} / {len(self.test_cases)}")
        
        # 清空文本框
        self.case_info_text.delete("1.0", tk.END)
        self.script_text.delete("1.0", tk.END)
        
        # 显示用例信息
        case_info = f"""用例名称: {case.get('name', 'N/A')}
测试目的: {case.get('purpose', 'N/A')}
前置条件: {case.get('preconditions', 'N/A')}
测试步骤: {case.get('steps', 'N/A')}
预期结果: {case.get('expected_result', 'N/A')}
测试数据: {case.get('test_data', 'N/A')}"""
        
        self.case_info_text.insert("1.0", case_info)
        
        # 显示测试脚本
        script = case.get('script', '无测试脚本')
        self.script_text.insert("1.0", script)

    def prev_case(self):
        """显示上一个测试用例"""
        if not self.test_cases:
            return
        
        if self.current_case_index > 0:
            self.current_case_index -= 1
            self._display_current_case()

    def next_case(self):
        """显示下一个测试用例"""
        if not self.test_cases:
            return
        
        if self.current_case_index < len(self.test_cases) - 1:
            self.current_case_index += 1
            self._display_current_case()

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

    def save_all_cases(self):
        """保存所有测试用例到文件"""
        if not self.test_cases:
            messagebox.showwarning("警告", "没有测试用例可保存")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存测试用例",
            defaultextension=".json",
            filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                gemini.save_test_cases_to_file(self.test_cases, file_path)
                messagebox.showinfo("成功", f"测试用例已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {e}")


if __name__ == "__main__":
    app = GeminiApp()
    app.mainloop()
