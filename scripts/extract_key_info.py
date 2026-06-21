#!/usr/bin/env python3
"""
合同关键信息提取工具 - 从合同文本中提取结构化关键信息。
用法: python extract_key_info.py <file_path> [--text "直接文本"]
输出: JSON格式的关键信息
"""

import sys
import json
import re
import argparse
from pathlib import Path


def extract_parties(text: str) -> list:
    """提取合同主体信息。"""
    parties = []

    patterns = [
        r'甲方[：:]\s*(.+?)(?:\n|$)',
        r'甲方[（(].*?[）)]\s*[：:]\s*(.+?)(?:\n|$)',
        r'出租方[：:]\s*(.+?)(?:\n|$)',
        r'买方[：:]\s*(.+?)(?:\n|$)',
        r'发包方[：:]\s*(.+?)(?:\n|$)',
        r'委托方[：:]\s*(.+?)(?:\n|$)',
        r'雇主[：:]\s*(.+?)(?:\n|$)',
        r'甲方.*?名称[：:]\s*(.+?)(?:\n|$)',
        r'Party A[：:]\s*(.+?)(?:\n|$)',
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            name = m.group(1).strip()
            if name and len(name) < 200:
                parties.append({"role": "甲方", "name": name})
            break

    patterns_b = [
        r'乙方[：:]\s*(.+?)(?:\n|$)',
        r'乙方[（(].*?[）)]\s*[：:]\s*(.+?)(?:\n|$)',
        r'承租方[：:]\s*(.+?)(?:\n|$)',
        r'卖方[：:]\s*(.+?)(?:\n|$)',
        r'承包方[：:]\s*(.+?)(?:\n|$)',
        r'受托方[：:]\s*(.+?)(?:\n|$)',
        r'雇员[：:]\s*(.+?)(?:\n|$)',
        r'乙方.*?名称[：:]\s*(.+?)(?:\n|$)',
        r'Party B[：:]\s*(.+?)(?:\n|$)',
    ]
    for p in patterns_b:
        m = re.search(p, text)
        if m:
            name = m.group(1).strip()
            if name and len(name) < 200:
                parties.append({"role": "乙方", "name": name})
            break

    # 提取统一社会信用代码
    credit_pattern = r'统一社会信用代码[：:]\s*([0-9A-Za-z]{18})'
    credits = re.findall(credit_pattern, text)
    for i, credit in enumerate(credits[:2]):
        if i < len(parties):
            parties[i]["credit_code"] = credit

    # 提取法定代表人
    legal_rep_pattern = r'法定代表人[：:]\s*(.+?)(?:\n|$)'
    legal_reps = re.findall(legal_rep_pattern, text)
    for i, rep in enumerate(legal_reps[:2]):
        if i < len(parties):
            parties[i]["legal_representative"] = rep.strip()

    return parties


def extract_amounts(text: str) -> list:
    """提取金额信息。"""
    amounts = []

    patterns = [
        (r'总\s*价[（(]含税[）)]?[）)]?\s*[：:]\s*(.+?)(?:\n|$)', '总价(含税)'),
        (r'总\s*价[（(]不含税[）)]?[）)]?\s*[：:]\s*(.+?)(?:\n|$)', '总价(不含税)'),
        (r'合同总\s*额\s*[：:]\s*(.+?)(?:\n|$)', '合同总额'),
        (r'合同价\s*款\s*[：:]\s*(.+?)(?:\n|$)', '合同价款'),
        (r'金\s*额\s*[：:]\s*(.+?)(?:\n|$)', '金额'),
        (r'租\s*金\s*[：:]\s*(.+?)(?:\n|$)', '租金'),
        (r'服\s*务\s*费\s*[：:]\s*(.+?)(?:\n|$)', '服务费'),
        (r'报\s*酬\s*[：:]\s*(.+?)(?:\n|$)', '报酬'),
        (r'工\s*资\s*[：:]\s*(.+?)(?:[\/\/月\n])', '工资'),
        (r'定\s*金\s*[：:]\s*(.+?)(?:\n|$)', '定金'),
        (r'保\s*证\s*金\s*[：:]\s*(.+?)(?:\n|$)', '保证金'),
        (r'首\s*付\s*[：:]\s*(.+?)(?:\n|$)', '首付'),
    ]

    for pattern, label in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            val = match.strip()
            if val and len(val) < 100:
                amounts.append({"type": label, "value": val})

    # 提取大写金额
    uppercase_pattern = r'大写[：:]\s*(.+?)(?:\n|$)'
    upper_matches = re.findall(uppercase_pattern, text)
    for match in upper_matches:
        val = match.strip()
        if val and len(val) < 100:
            amounts.append({"type": "大写金额", "value": val})

    return amounts


def extract_dates(text: str) -> list:
    """提取关键日期信息。"""
    dates = []

    patterns = [
        (r'签\s*订\s*日\s*期\s*[：:]\s*(.+?)(?:\n|$)', '签订日期'),
        (r'签\s*订\s*时\s*间\s*[：:]\s*(.+?)(?:\n|$)', '签订时间'),
        (r'合\s*同\s*期\s*限\s*[：:]\s*(.+?)(?:\n|$)', '合同期限'),
        (r'有\s*效\s*期\s*限\s*[：:]\s*(.+?)(?:\n|$)', '有效期限'),
        (r'履\s*行\s*期\s*限\s*[：:]\s*(.+?)(?:\n|$)', '履行期限'),
        (r'交\s*货\s*期\s*[：:]\s*(.+?)(?:\n|$)', '交货期'),
        (r'交\s*付\s*时\s*间\s*[：:]\s*(.+?)(?:\n|$)', '交付时间'),
        (r'开\s*工\s*日\s*期\s*[：:]\s*(.+?)(?:\n|$)', '开工日期'),
        (r'竣\s*工\s*日\s*期\s*[：:]\s*(.+?)(?:\n|$)', '竣工日期'),
        (r'试\s*用\s*期\s*[：:]\s*(.+?)(?:\n|$)', '试用期'),
        (r'起\s*止\s*日\s*期\s*[：:]\s*(.+?)(?:\n|$)', '起止日期'),
        (r'自\s*(\d{4}年\d{1,2}月\d{1,2}日).*?至\s*(\d{4}年\d{1,2}月\d{1,2}日)', '起止时间'),
    ]

    for pattern, label in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if isinstance(match, tuple):
                val = f"自{match[0]}至{match[1]}"
            else:
                val = match.strip()
            if val and len(val) < 100:
                dates.append({"type": label, "value": val})

    # 通用日期提取 (YYYY年MM月DD日 或 YYYY-MM-DD 或 YYYY/MM/DD)
    general_dates = re.findall(r'(\d{4}[-/年]\d{1,2}[-/月]\d{1,2}日?)', text)
    for d in general_dates[:10]:
        if not any(d in existing["value"] for existing in dates):
            dates.append({"type": "文中日期", "value": d})

    return dates


def extract_payment_terms(text: str) -> list:
    """提取付款条款。"""
    terms = []

    patterns = [
        (r'(第[一二三四五六七八九十]+期?付款.*?)(?:\n\n|\n第[一二三四五六七八九十]+期)', '分期付款'),
        (r'付款\s*方\s*式\s*[：:]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)', '付款方式'),
        (r'支\s*付\s*方\s*式\s*[：:]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)', '支付方式'),
        (r'结\s*算\s*方\s*式\s*[：:]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)', '结算方式'),
        (r'发\s*票\s*类\s*型\s*[：:]\s*(.+?)(?:\n|$)', '发票类型'),
        (r'开\s*票\s*时\s*间\s*[：:]\s*(.+?)(?:\n|$)', '开票时间'),
    ]

    for pattern, label in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            val = match.strip() if isinstance(match, str) else " ".join(match).strip()
            if val and len(val) < 500:
                terms.append({"type": label, "value": val[:200]})

    return terms


def extract_obligations(text: str) -> dict:
    """提取权利义务概要。"""
    obligations = {"party_a": [], "party_b": []}

    # 甲方义务
    a_patterns = [
        r'甲方.*?义务.*?[:：]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
        r'甲方.*?权\s*利.*?[:：]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
        r'甲方.*?应\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
    ]
    for p in a_patterns:
        matches = re.findall(p, text, re.DOTALL)
        for m in matches[:5]:
            val = m.strip()[:200]
            if val:
                obligations["party_a"].append(val)

    # 乙方义务
    b_patterns = [
        r'乙方.*?义务.*?[:：]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
        r'乙方.*?权\s*利.*?[:：]\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
        r'乙方.*?应\s*(.+?)(?:\n\n|\n[一二三四五六七八九十]、)',
    ]
    for p in b_patterns:
        matches = re.findall(p, text, re.DOTALL)
        for m in matches[:5]:
            val = m.strip()[:200]
            if val:
                obligations["party_b"].append(val)

    return obligations


def extract_breach_clauses(text: str) -> list:
    """提取违约责任条款。"""
    clauses = []

    # 查找违约责任章节
    pattern = r'(?:违约责任|违约条款)[\s\S]*?(?=\n[一二三四五六七八九十]+、|\n第[一二三四五六七八九十]+条|$)'
    match = re.search(pattern, text)
    if match:
        section = match.group(0)
        # 提取具体违约条款
        clause_pattern = r'([一二三四五六七八九十]+[、.]\s*.+?)(?=[一二三四五六七八九十]+[、.]|$)'
        sub_matches = re.findall(clause_pattern, section, re.DOTALL)
        for m in sub_matches:
            val = m.strip()[:300]
            if val and len(val) > 10:
                clauses.append(val)

    if not clauses and match:
        clauses.append(match.group(0).strip()[:500])

    return clauses


def extract_dispute_resolution(text: str) -> dict:
    """提取争议解决条款。"""
    result = {"method": "", "jurisdiction": "", "arbitration": ""}

    # 诉讼 vs 仲裁
    if re.search(r'仲裁', text):
        result["method"] = "仲裁"
        arb_match = re.search(r'(\S+仲裁委员会)', text)
        if arb_match:
            result["arbitration"] = arb_match.group(1)
    elif re.search(r'诉讼|法院|管辖', text):
        result["method"] = "诉讼"
        court_match = re.search(r'(\S+人民法院)', text)
        if court_match:
            result["jurisdiction"] = court_match.group(1)

    # 管辖约定
    jurisdiction_patterns = [
        r'管辖[：:]\s*(.+?)(?:\n|$)',
        r'管辖法院[：:]\s*(.+?)(?:\n|$)',
        r'向\s*(.+?人民法院)\s*提起',
    ]
    for p in jurisdiction_patterns:
        m = re.search(p, text)
        if m:
            result["jurisdiction"] = m.group(1).strip()
            break

    return result


def extract_confidentiality(text: str) -> dict:
    """提取保密条款信息。"""
    result = {"has_confidentiality": False, "confidentiality_period": "", "details": ""}

    if re.search(r'保密|商业秘密|机密', text):
        result["has_confidentiality"] = True

        period_match = re.search(r'保密期[限间][：:]\s*(.+?)(?:\n|$)', text)
        if period_match:
            result["confidentiality_period"] = period_match.group(1).strip()

        detail_match = re.search(r'(保密[\s\S]*?)(?=\n[一二三四五六七八九十]+、|\n第[一二三四五六七八九十]+条|$)', text)
        if detail_match:
            result["details"] = detail_match.group(1).strip()[:300]

    return result


def extract_contract_name(text: str) -> str:
    """提取合同名称。"""
    # 尝试从第一行提取
    first_lines = text.strip().split('\n')[:5]
    for line in first_lines:
        line = line.strip()
        if re.search(r'合同|协议|契约|约定', line) and len(line) < 50:
            return line

    # 尝试从标题提取
    title_match = re.search(r'【(.+?)】', text)
    if title_match:
        return title_match.group(1)

    return "未识别合同名称"


def extract_clauses(text: str) -> list:
    """将合同文本结构化为条款列表。"""
    clauses = []

    # 匹配 "第X条" 格式
    pattern = r'第([一二三四五六七八九十百千\d]+)条\s*[、.::]?\s*(.+?)(?=第[一二三四五六七八九十百千\d]+条|$)'
    matches = re.findall(pattern, text, re.DOTALL)

    for num, content in matches:
        content = content.strip()
        # 提取条款标题（第一行或冒号前内容）
        title = ""
        if '：' in content[:50] or ':' in content[:50]:
            title = content.split('：')[0].split(':')[0].strip()
        elif '\n' in content[:80]:
            title = content.split('\n')[0].strip()

        clauses.append({
            "number": num,
            "title": title[:100] if title else f"第{num}条",
            "content": content[:500]
        })

    # 如果没有匹配到"第X条"，尝试"一、"格式
    if not clauses:
        pattern2 = r'([一二三四五六七八九十]+)[、.]\s*(.+?)(?=[一二三四五六七八九十]+[、.]|$)'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        for num, content in matches2:
            content = content.strip()
            title = content.split('\n')[0].strip()[:100] if '\n' in content else content[:100]
            clauses.append({
                "number": num,
                "title": title,
                "content": content[:500]
            })

    return clauses


def generate_summary(key_info: dict) -> str:
    """生成合同摘要。"""
    parts = []

    name = key_info.get("contract_name", "未识别")
    parts.append(f"本合同为《{name}》")

    # 主体
    parties = key_info.get("parties", [])
    if parties:
        party_str = "、".join([f"{p['role']}：{p['name']}" for p in parties])
        parts.append(f"，签约主体为{party_str}")

    # 金额
    amounts = key_info.get("amounts", [])
    if amounts:
        primary_amount = amounts[0]
        parts.append(f"，{primary_amount['type']}为{primary_amount['value']}")

    # 期限
    dates = key_info.get("dates", [])
    for d in dates:
        if d["type"] in ["合同期限", "有效期限", "履行期限", "起止时间"]:
            parts.append(f"，{d['type']}为{d['value']}")
            break

    # 争议解决
    dispute = key_info.get("dispute_resolution", {})
    if dispute.get("method"):
        method_text = "仲裁" if dispute["method"] == "仲裁" else "诉讼"
        jurisdiction = dispute.get("jurisdiction") or dispute.get("arbitration", "")
        if jurisdiction:
            parts.append(f"，争议解决方式为{method_text}（{jurisdiction}）")
        else:
            parts.append(f"，争议解决方式为{method_text}")

    parts.append("。")
    return "".join(parts)


def main():
    parser = argparse.ArgumentParser(description='合同关键信息提取工具')
    parser.add_argument('filepath', nargs='?', help='合同文件路径 (.txt)')
    parser.add_argument('--text', help='直接传入合同文本')
    parser.add_argument('--output', '-o', help='输出JSON文件路径')

    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.filepath:
        filepath = Path(args.filepath)
        if not filepath.exists():
            sys.exit(f"ERROR: File not found: {args.filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        sys.exit("ERROR: 需要提供文件路径或--text参数")

    # 提取所有关键信息
    key_info = {
        "contract_name": extract_contract_name(text),
        "parties": extract_parties(text),
        "amounts": extract_amounts(text),
        "dates": extract_dates(text),
        "payment_terms": extract_payment_terms(text),
        "obligations": extract_obligations(text),
        "breach_clauses": extract_breach_clauses(text),
        "dispute_resolution": extract_dispute_resolution(text),
        "confidentiality": extract_confidentiality(text),
        "clauses": extract_clauses(text),
    }

    # 生成摘要
    key_info["summary"] = generate_summary(key_info)

    # 统计
    key_info["stats"] = {
        "clause_count": len(key_info["clauses"]),
        "party_count": len(key_info["parties"]),
        "amount_count": len(key_info["amounts"]),
        "date_count": len(key_info["dates"]),
        "text_length": len(text),
        "has_confidentiality": key_info["confidentiality"]["has_confidentiality"],
    }

    output = json.dumps(key_info, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"关键信息已保存到: {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
