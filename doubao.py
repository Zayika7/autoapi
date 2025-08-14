import requests
import json
import time
import os
import re
import base64
import hashlib
import hmac

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    print("警告: 未安装openai库，请运行: pip install openai")
    OPENAI_AVAILABLE = False

DOUBAO_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DOUBAO_CHAT_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
DOUBAO_API_KEY = None  # 用户必须通过环境变量或GUI配置

def get_doubao_appkey():
    """获取豆包的appkey（需要用户手动配置或通过抓包获取）"""
    # 优先从环境变量获取
    api_key = os.environ.get("DOUBAO_API_KEY")
    if api_key:
        return api_key
    
    # 如果没有环境变量，返回None，提示用户配置
    if not DOUBAO_API_KEY:
        print("警告: 未配置豆包API密钥")
        print("请通过以下方式配置:")
        print("1. 在环境变量中设置 DOUBAO_API_KEY")
        print("2. 或在GUI界面中输入API密钥")
        return None
    return DOUBAO_API_KEY

def call_doubao_api(prompt: str, model: str = "doubao-seed-1-6-250615") -> str:
    """调用豆包API生成内容"""
    api_key = get_doubao_appkey()
    if not api_key:
        print("豆包API密钥未配置")
        return ""
    
    if not OPENAI_AVAILABLE:
        print("openai库未安装，无法调用API")
        return ""
    
    try:
        print(f">>> 正在请求豆包API设计智能测试用例，请稍候...")
        print(f"使用模型: {model}")
        
        # 使用openai库调用豆包API
        client = OpenAI(
            base_url=DOUBAO_BASE_URL,
            api_key=api_key,
        )
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content
            print(f"<<< 豆包API成功设计了测试用例！")
            return content
        else:
            print("豆包API返回格式异常")
            return ""
            
    except Exception as e:
        print(f"调用豆包API失败: {e}")
        return ""

def call_doubao_api_fallback(prompt: str, model: str = "doubao-seed-1-6-250615") -> str:
    """备用方法：直接HTTP调用豆包API"""
    api_key = get_doubao_appkey()
    if not api_key:
        print("豆包API密钥未配置")
        return ""
    
    # 豆包官方API端点（火山引擎豆包服务）
    api_endpoints = [
        "https://api.volcengine.com/ark/v3/chat/completions",
        "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 根据豆包API文档，使用正确的请求格式
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }
    
    for endpoint in api_endpoints:
        try:
            print(f">>> 正在请求豆包API ({endpoint}) 设计智能测试用例，请稍候...")
            print(f"使用模型: {model}")
            response = requests.post(endpoint, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                print(f"<<< 豆包API成功设计了测试用例！")
                return content
            else:
                print(f"豆包API返回格式异常: {result}")
                continue
                
        except requests.exceptions.ConnectionError as e:
            print(f"连接失败 {endpoint}: {e}")
            continue
        except Exception as e:
            print(f"调用豆包API失败 {endpoint}: {e}")
            continue
    return ""

def design_knowledge_driven_cases(api_doc: dict, test_data_json: str, model: str = "doubao-seed-1-6-250615") -> list:
    """使用豆包API，结合API文档和预设业务数据，设计出引用环境变量的测试用例。"""
    if not api_doc:
        return []

    # 使用与gemini.py相同的prompt模板
    prompt_template = """
    你是一位顶尖的中文测试开发专家。你的任务是基于我提供的API文档和一套已有的测试环境变量，设计出高质量、有业务价值的测试用例。

    **第一部分：这是你要测试的API的文档。**
    ```json
    {api_doc_json}
    ```

    **第二部分：这是你可以使用的、包含真实业务含义的【测试环境变量库】。**
    ```json
    {test_data_json}
    ```

    **第三部分：这些是 `args` 中引用的复杂对象模型文档（当存在时）。**
    - 你需要基于这些模型的字段来构建对应参数（如 query_body、query_extend）的 JSON 结构。
    - 仅使用与业务有关的必需或常用字段，避免无意义的冗余字段。
    ```json
    {related_models_json}
    ```

    **你的核心工作方法和原则：**
    1.  **用例范围**：只设计 `args` 部分的业务参数。**完全不需要考虑 `_app`, `_t`, `_sign`, `_sign_kind` 等系统参数**，它们由框架自动处理。
    2.  **智能映射是关键！** 你需要深刻理解API参数的含义（参考其`description`），然后在【测试环境变量库】中找到`description`最匹配的变量。
        - **示例**：如果API参数`goods`的描述是"(系统)商品编码"，你应该在库中寻找，并发现变量`goodcode`的描述是"open测试普通商品编码"，因此你知道在测试普通商品场景时，应该使用`goodcode`。
    3.  **使用引用格式！** 当你决定使用一个环境变量时，在最终的`parameters`对象中，必须使用`${{变量名}}`的格式来引用它。
        - **示例**：为`goods`参数赋值时，应写为`"goods": "${{goodcode}}"`。
    4.  **设计业务场景！** 创造有意义的组合，而不是测试无用的技术细节。例如：
        - 设计一个"【专项】查询序列号商品"的用例，此时`goods`参数就应该引用`${{goodcode_sn}}`。
        - 设计一个"【组合】查询特定B2C店铺的组合商品"的用例，此时`shop_nick`应引用`${{b2c_shopNick}}`，`goods`应引用`${{coproduct}}`。
    5.  **特殊参数**：
        -   **`page`和`limit`**：完全不需要为它们设计边界值或异常用例。在所有用例中，如果需要，请默认使用 `page=1` 和 `limit=20` 的**字面量值**。
    6.  **负向用例同样重要**：
        -   业务规则违反（例如，"shop_name和shop_nick不能同时为空"的场景）。
        -   **创造性负向**：对于需要测试"不存在的"或"非法"场景的负向用例，你可以**合理地创造**符合数据类型和长度的**具体虚拟值**（例如`"shop_nick": "non_existent_shop_12345"`）。

    **最终输出格式（必须严格遵守）：**
    - 你的整个回答必须是一个**纯粹的、合法的JSON数组**。
    - `case_name`键的值**必须是中文**，简洁明了，能体现测试目的。
    - `parameters`键的值是一个对象，其键值对必须遵循上述的**引用格式**（`page`, `limit`, 和创造性负向用例的值除外）。
    """

    # 采集复杂对象模型文档，用于增强提示
    related_models = collect_related_models(api_doc)

    prompt = prompt_template.format(
        api_doc_json=json.dumps(api_doc, indent=2),
        test_data_json=test_data_json,
        related_models_json=json.dumps(related_models, ensure_ascii=False, indent=2)
    )

    try:
        raw_text = call_doubao_api(prompt, model)
        
        if not raw_text:
            print("豆包API未返回有效内容")
            return []

        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)

        if not json_match:
            print("在豆包API的响应中未能找到有效的JSON数组。")
            print("原始响应内容:", raw_text[:1000])
            return []

        json_string = json_match.group(0)
        test_cases = json.loads(json_string)

        print(f"<<< 豆包API成功设计了 {len(test_cases)} 个智能测试用例！")
        return test_cases
    except Exception as e:
        print(f"\n调用或解析豆包API时出错: {e}")
        return []

def collect_related_models(api_doc: dict) -> dict:
    """收集 args 中包含 type.url 的复杂对象模型，返回 {param_name: model_doc}。"""
    models: dict = {}
    try:
        args = api_doc.get("request", {}).get("args", [])
        for arg in args:
            if not isinstance(arg, dict):
                continue
            name = arg.get("name")
            t = arg.get("type")
            if not name or not isinstance(t, dict):
                continue
            url = t.get("url")
            if not url:
                continue
            try:
                resp = requests.get(url, timeout=20)
                resp.raise_for_status()
                models[name] = resp.json()
            except Exception as fetch_err:
                # 失败时跳过，不影响主流程
                models[name] = {"_error": f"fetch_failed: {fetch_err}", "url": url}
    except Exception:
        pass
    return models

def get_api_doc(api_path: str) -> dict:
    """获取API文档"""
    BASE_DOC_URL = "http://114.67.231.162/api/doc"
    doc_url = f"{BASE_DOC_URL}{api_path}"
    try:
        response = requests.get(doc_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取或解析API文档失败 {api_path}: {e}")
        return None

def load_test_data(file_path: str) -> str:
    """加载测试数据文件"""
    try:
        # 处理相对路径和绝对路径
        if not os.path.isabs(file_path):
            # 如果是相对路径，尝试从当前工作目录查找
            current_dir = os.getcwd()
            full_path = os.path.join(current_dir, file_path)
        else:
            full_path = file_path
            
        # 检查文件是否存在
        if not os.path.exists(full_path):
            print(f"测试数据文件不存在: {full_path}")
            return "[]"
            
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 验证数据格式
        if not isinstance(data, list):
            print(f"测试数据文件格式错误，应为JSON数组: {file_path}")
            return "[]"
            
        simplified_data = [
            {"name": item.get("name"), "value": item.get("value"), "description": item.get("description", "")}
            for item in data
        ]
        
        print(f"成功加载测试数据文件: {full_path} ({len(simplified_data)} 条数据)")
        return json.dumps(simplified_data, ensure_ascii=False, indent=2)
        
    except json.JSONDecodeError as e:
        print(f"JSON格式错误 '{file_path}': {e}")
        return "[]"
    except Exception as e:
        print(f"读取或处理测试数据文件 '{file_path}' 失败: {e}")
        return "[]"

def generate_scripts_for_case(api_doc: dict, test_case: dict) -> str:
    """为单个测试用例生成最终正确的BeanShell脚本和请求体"""
    case_name = test_case.get("case_name", "未命名用例")
    case_params = test_case.get("parameters", {})
    api_args = api_doc.get("request", {}).get("args", [])

    # 准备业务参数部分
    business_param_parts = []
    # 记录需要覆盖写入 BeanShell 变量定义的特殊字面量（如复杂对象参数）
    special_literal_overrides = {}
    for param_def in api_args:
        name = param_def['name']
        if name in case_params:
            value = case_params[name]

            # 若参数类型含有 URL（表示是一个模型/复杂对象），则按 JSON 对待并进行"压缩+转义"
            param_type = param_def.get('type') if isinstance(param_def.get('type'), dict) else None
            if isinstance(param_type, dict) and param_type.get('url'):
                # 对字面量值进行规范化，并存入 vars，再在签名/请求体使用 ${__urlencode(${var})}
                if not (isinstance(value, str) and value.startswith('${')):
                    normalized = _normalize_json_like_to_compact_text(value)
                    special_literal_overrides[name] = normalized
                business_param_parts.append(f"{name}=${{__urlencode(${{{name}}})}}")
                continue

            # 根据值的类型决定格式
            if isinstance(value, str) and value.startswith('${'):
                # 对于变量引用
                if name == 'page' or name == 'limit': # 理论上不会走到这里，但作为保险
                    business_param_parts.append(f"{name}={value}")
                else:
                    business_param_parts.append(f"{name}=${{__urlencode({value})}}")
            else:
                # 对于字面量值 (page, limit, 或AI创造的负向用例值)
                business_param_parts.append(f"{name}={value}")

    sorted_business_params = sorted(business_param_parts, key=lambda p: p.split('=')[0])
    sorted_business_params_str = '&'.join(sorted_business_params)

    # 1. 定义用例数据 (第一个前置脚本)
    # 只为AI创造的字面量值（非变量引用）定义vars.put
    beanshell_vars_def = []
    for name, value in sorted(case_params.items()):
        if not (isinstance(value, str) and value.startswith('${')):
            # 若存在特殊覆盖（例如已压缩/标准化的 query_body），优先使用覆盖值
            value_to_store = special_literal_overrides.get(name, value)
            escaped_value = str(value_to_store).replace('\\', '\\\\').replace('"', '\\"')
            beanshell_vars_def.append(f'vars.put("{name}", "{escaped_value}");')

    # 2. 生成签名逻辑 (第二个前置脚本)
    beanshell_sign_builder_parts = []
    for part in sorted_business_params:
        param_name, value_str = (part.split('=', 1) + [''])[:2]

        if value_str.startswith('${'): # 如果是变量引用
            env_var_name = re.search(r'\${(.*)}', value_str).group(1)
            # 对于被__urlencode包裹的，提取内部的变量名
            if "__urlencode" in env_var_name:
                env_var_name = re.search(r'\${(.*)}', env_var_name).group(1)

            if param_name == 'page' or param_name == 'limit':
                beanshell_sign_builder_parts.append(f'if (vars.get("{env_var_name}") != null) {{ paramParts.add("{param_name}=" + vars.get("{env_var_name}")); }}')
            else:
                beanshell_sign_builder_parts.append(f'if (vars.get("{env_var_name}") != null) {{ paramParts.add("{param_name}=" + URLEncoder.encode(vars.get("{env_var_name}"), "UTF-8")); }}')
        else: # 对于字面量值
            beanshell_sign_builder_parts.append(f'paramParts.add("{part}");')

    pre_script_template = f"""
import java.security.MessageDigest;
import java.net.URLEncoder;
import java.util.ArrayList;

ArrayList paramParts = new ArrayList();
{chr(10).join(beanshell_sign_builder_parts)}

StringBuffer argsBodyBuffer = new StringBuffer();
for (int i = 0; i < paramParts.size(); i++) {{
    argsBodyBuffer.append(paramParts.get(i));
    if (i < paramParts.size() - 1) {{
        argsBodyBuffer.append("&");
    }}
}}
String argsBody = argsBodyBuffer.toString();

String time = String.valueOf(System.currentTimeMillis() / 1000);
String stringToSign = vars.get("secret") + "_app=" + vars.get("appKey") + "&_s=&_t=" + time + "&" + argsBody + vars.get("secret");

log.info("String to sign: " + stringToSign);

MessageDigest md = MessageDigest.getInstance("MD5");
byte[] digest = md.digest(stringToSign.getBytes("UTF-8"));
StringBuffer sb = new StringBuffer();
for (int i = 0; i < digest.length; ++i) {{
    sb.append(Integer.toHexString((digest[i] & 0xFF) | 0x100).substring(1,3));
}}
String signature = sb.toString().toUpperCase();
vars.put("signature", signature);
vars.put("time", time);
"""

    # 3. 准备请求体
    request_body_text = f"_app=${{appKey}}&_s=&_sign=${{signature}}&_t=${{time}}&{sorted_business_params_str}"

    # 组合输出
    output_lines = []
    output_lines.append(f"\n--- 用例: {case_name} ---")
    # 只有在需要定义字面量变量时，才生成第一个前置脚本
    if beanshell_vars_def:
        output_lines.append("------------------------------------------------------------")
        output_lines.append("(1) 前置脚本 (JSR223PreProcessor - 定义数据)")
        output_lines.append("------------------------------------------------------------")
        output_lines.append("```beanshell")
        output_lines.append('\n'.join(beanshell_vars_def))
        output_lines.append("```\n")

    output_lines.append("------------------------------------------------------------")
    output_lines.append("(2) 前置脚本 (JSR223PreProcessor - 计算签名)")
    output_lines.append("------------------------------------------------------------")
    output_lines.append("```beanshell")
    output_lines.append(pre_script_template.strip())
    output_lines.append("```\n")
    output_lines.append("------------------------------------------------------------")
    output_lines.append("(3) 请求体 (Raw)")
    output_lines.append("------------------------------------------------------------")
    output_lines.append("```text")
    output_lines.append(request_body_text)
    output_lines.append("```")

    return "\n".join(output_lines)

def _normalize_json_like_to_compact_text(value) -> str:
    """将 dict/list 或 JSON/类JSON 字符串统一为双引号的紧凑 JSON 文本。"""
    try:
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
        if isinstance(value, str):
            # 先尝试当作合法 JSON
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, ensure_ascii=False, separators=(',', ':'))
            except Exception:
                # 简单容错：单引号替换为双引号，并去除多余空白
                tmp = value.replace("'", '"')
                tmp = re.sub(r"\s+", "", tmp)
                return tmp
        # 其他类型，按 JSON 序列化
        return json.dumps(value, ensure_ascii=False, separators=(',', ':'))
    except Exception:
        # 兜底：转字符串
        return str(value)

# --- 测试函数 ---
def test_doubao_connection():
    """测试豆包API连接和基本功能"""
    if not DOUBAO_API_KEY:
        print("豆包API密钥未配置")
        return False
    
    try:
        print(">>> 测试豆包API连接...")
        simple_prompt = "请回答：1+1等于几？"
        response = call_doubao_api(simple_prompt)
        
        if response:
            print("成功获取响应文本:", response)
            return True
        else:
            print("豆包API未返回有效响应")
            return False
            
    except Exception as e:
        print(f"测试豆包API失败: {e}")
        return False

# --- 主执行函数 ---
if __name__ == "__main__":
    # 首先测试豆包连接
    if test_doubao_connection():
        print("\n豆包API连接正常，继续执行主程序...")
        
        env_file_path = "MS_25_Environments_variables.json"
        test_data = load_test_data(env_file_path)

        if test_data != "[]":
            target_api_path = "/erp/opentrade/modify/order/batchmodifywarehouse"
            api_doc = get_api_doc(target_api_path)

            if api_doc:
                test_cases = design_knowledge_driven_cases(api_doc, test_data)

                if not test_cases:
                    print("\n未能从豆包API获取测试用例。")
                else:
                    print("\n============================================================")
                    print(f"==  开始为接口 {target_api_path} 生成业务用例脚本...")
                    print("============================================================")
                    for case in test_cases:
                        script_block = generate_scripts_for_case(api_doc, case)
                        print(script_block)
    else:
        print("\n豆包API连接失败，请检查配置和网络连接") 