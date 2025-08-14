import requests
import json
import time
import os
import re
import google.generativeai as genai

BASE_DOC_URL = "http://114.67.231.162/api/doc"

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("警告: 未找到环境变量 GEMINI_API_KEY。请在PyCharm运行配置中设置。")
    genai.configure(api_key=api_key)
    gemini_model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    print(f"Gemini 初始化失败: {e}")
    gemini_model = None

def get_api_doc(api_path: str) -> dict:
    """获取API文档信息"""
    doc_url = f"{BASE_DOC_URL}{api_path}"
    try:
        response = requests.get(doc_url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"获取或解析API文档失败 {api_path}: {e}")
        return None

def load_test_data(file_path: str) -> str:
    """加载并简化测试数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        simplified_data = [
            {"name": item.get("name"), "value": item.get("value"), "description": item.get("description", "")}
            for item in data
        ]
        return json.dumps(simplified_data, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"读取或处理测试数据文件 '{file_path}' 失败: {e}")
        return "[]"

def design_knowledge_driven_cases(api_doc: dict, test_data_json: str) -> list:
    """使用Gemini，结合API文档和预设业务数据，设计出引用环境变量的测试用例。"""
    if not gemini_model or not api_doc:
        return []

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

    **你的核心工作方法和原则：**
    1.  **用例范围**：只设计 `args` 部分的业务参数。**完全不需要考虑 `_app`, `_t`, `_sign`, `_sign_kind` 等系统参数**，它们由框架自动处理。
    2.  **智能映射是关键！** 你需要深刻理解API参数的含义（参考其`description`），然后在【测试环境变量库】中找到`description`最匹配的变量。
        - **示例**：如果API参数`goods`的描述是“(系统)商品编码”，你应该在库中寻找，并发现变量`goodcode`的描述是“open测试普通商品编码”，因此你知道在测试普通商品场景时，应该使用`goodcode`。
    3.  **使用引用格式！** 当你决定使用一个环境变量时，在最终的`parameters`对象中，必须使用`${{变量名}}`的格式来引用它。
        - **示例**：为`goods`参数赋值时，应写为`"goods": "${{goodcode}}"`。
    4.  **设计业务场景！** 创造有意义的组合，而不是测试无用的技术细节。例如：
        - 设计一个“【专项】查询序列号商品”的用例，此时`goods`参数就应该引用`${{goodcode_sn}}`。
        - 设计一个“【组合】查询特定B2C店铺的组合商品”的用例，此时`shop_nick`应引用`${{b2c_shopNick}}`，`goods`应引用`${{coproduct}}`。
    5.  **特殊参数**：
        -   **`page`和`limit`**：完全不需要为它们设计边界值或异常用例。在所有用例中，如果需要，请默认使用 `page=1` 和 `limit=20` 的**字面量值**。
    6.  **负向用例同样重要**：
        -   业务规则违反（例如，“shop_name和shop_nick不能同时为空”的场景）。
        -   **创造性负向**：对于需要测试“不存在的”或“非法”场景的负向用例，你可以**合理地创造**符合数据类型和长度的**具体虚拟值**（例如`"shop_nick": "non_existent_shop_12345"`）。

    **最终输出格式（必须严格遵守）：**
    - 你的整个回答必须是一个**纯粹的、合法的JSON数组**。
    - `case_name`键的值**必须是中文**，简洁明了，能体现测试目的。
    - `parameters`键的值是一个对象，其键值对必须遵循上述的**引用格式**（`page`, `limit`, 和创造性负向用例的值除外）。
    """

    prompt = prompt_template.format(
        api_doc_json=json.dumps(api_doc, indent=2),
        test_data_json=test_data_json
    )

    print("\n>>> 正在请求 Gemini 设计智能测试用例，请稍候...")
    try:
        request_options = {"timeout": 120}
        response = gemini_model.generate_content(prompt, request_options=request_options)

        raw_text = response.text
        json_match = re.search(r'\[.*\]', raw_text, re.DOTALL)

        if not json_match:
            print("【错误】在Gemini的响应中未能找到有效的JSON数组。")
            return []

        json_string = json_match.group(0)
        test_cases = json.loads(json_string)

        print(f"<<< Gemini 成功设计了 {len(test_cases)} 个智能测试用例！")
        return test_cases
    except Exception as e:
        print(f"\n调用或解析Gemini API时出错: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print("Gemini 原始响应(部分):", response.text[:500])
        return []


def generate_scripts_for_case(api_doc: dict, test_case: dict) -> str:
    """为单个测试用例生成最终正确的BeanShell脚本和请求体"""
    case_name = test_case.get("case_name", "未命名用例")
    case_params = test_case.get("parameters", {})
    api_args = api_doc.get("request", {}).get("args", [])

    # 准备业务参数部分
    business_param_parts = []
    for param_def in api_args:
        name = param_def['name']
        if name in case_params:
            value = case_params[name]
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
            escaped_value = str(value).replace('\\', '\\\\').replace('"', '\\"')
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

if __name__ == "__main__":
    env_file_path = "MS_25_Environments_variables.json"
    test_data = load_test_data(env_file_path)

    if test_data != "[]":
        target_api_path = "/erp/opentrade/encry/info"
        api_doc = get_api_doc(target_api_path)

        if api_doc:
            test_cases = design_knowledge_driven_cases(api_doc, test_data)

            if not test_cases:
                print("\n未能从Gemini获取测试用例。")
            else:
                print("\n============================================================")
                print(f"==  开始为接口 {target_api_path} 生成业务用例脚本...")
                print("============================================================")
                for case in test_cases:
                    script_block = generate_scripts_for_case(api_doc, case)
                    print(script_block)