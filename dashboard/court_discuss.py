"""
朝堂议政引擎 — 多官员实时讨论系统

灵感来源于 nvwa 项目的 group_chat + crew_engine
将官员可视化 + 实时讨论 + 用户（皇帝）参与融合到三省六部

功能:
  - 选择官员参与议政
  - 围绕旨意/议题进行多轮群聊讨论
  - 皇帝可随时发言、下旨干预（天命降临）
  - 命运骰子：随机事件
  - 每个官员保持自己的角色性格和说话风格
"""

import json
import logging
import os
import time
import uuid

logger = logging.getLogger('court_discuss')

# ── 团队角色设定 ──

OFFICIAL_PROFILES = {
    'pmo': {
        'name': 'PMO', 'emoji': '📋', 'role': '项目管理',
        'duty': '项目全生命周期管理、资源协调与进度管控。负责需求分拣、立项及最终上线确认。',
        'personality': '专业、严谨、关注效率与合规。擅长多任务调度和风险预警。',
        'speaking_style': '专业干练，经常提到"进度"、"资源"、"风险"和"里程碑"。'
    },
    'product': {
        'name': '产品经理', 'emoji': '💡', 'role': '产品定义',
        'duty': '需求分析、方案规划与PRD输出。将业务需求转化为可落地的技术方案，并推动研发流程。',
        'personality': '洞察力强，擅长平衡业务价值与实现成本。逻辑性极强。',
        'speaking_style': '喜欢谈"用户价值"、"闭环"、"交互逻辑"，常说"从产品角度来看"。'
    },
    'ui': {
        'name': 'UI设计师', 'emoji': '🎨', 'role': '交互视觉',
        'duty': '交互设计、UI界面输出与用户体验优化。负责视觉规范和设计系统维护。',
        'personality': '追求极致美感与易用性，对细节有强迫症。关注品牌一致性。',
        'speaking_style': '经常提到"视觉层次"、"用户心智"、"组件化"、"适配"。'
    },
    'frontend': {
        'name': '前端工程师', 'emoji': '💻', 'role': '前端开发',
        'duty': '页面开发、交互实现与性能优化。负责前端框架维护和跨端适配。',
        'personality': '关注新技术，注重代码质量和工程化。喜欢谈论性能和兼容性。',
        'speaking_style': '常说"渲染性能"、"状态管理"、"工程化构建"、"响应式"。'
    },
    'backend': {
        'name': '后端工程师', 'emoji': '⚙️', 'role': '后端开发',
        'duty': '接口开发、逻辑实现与数据建模。负责系统架构设计、数据库优化及高并发处理。',
        'personality': '稳重、严谨，极其关注系统稳定性和数据安全性。',
        'speaking_style': '经常提到"高并发"、"一致性"、"幂等性"、"索引优化"。'
    },
    'qa': {
        'name': '测试工程师', 'emoji': '🧪', 'role': '质量保证',
        'duty': '功能测试、性能测试与自动化测试。负责发布前的质量把控与回归验证。',
        'personality': '细心、挑剔，善于发现隐藏的边界问题和潜在风险。',
        'speaking_style': '常说"边界条件"、"回归测试"、"压测数据"、"不通过"。'
    },
    'ops': {
        'name': '运维工程师', 'emoji': '🚀', 'role': '运维部署',
        'duty': '环境部署、CI/CD流水线、服务器监控与安全。负责系统的发布上线与扩缩容。',
        'personality': '冷静、果断，危机意识极强。是系统最后一道防线。',
        'speaking_style': '关注"可用性"、"回滚"、"资源利用率"、"监控告警"。'
    },
}

# ── 命运骰子事件（现代技术版）──

FATE_EVENTS = [
    '紧急告警：核心数据库负载过高，所有人必须参与讨论应急方案',
    '首席架构师：发现现有方案存在架构缺陷，建议重新评估',
    '技术沙龙分享：带来了一个全新的开源组件，可能改变实现思路',
    '代码审计发现计划中一个被忽视的严重安全漏洞',
    '老板发话：由于业务调整，该项目优先级提升，可以申请更多资源',
    '资深专家分享：针对当前问题分享了类似系统的成功处理经验',
    '用户反馈突变：用户对该功能的需求方向发生了180度转变',
    '竞争对手动态：竞品上线了类似功能，我们需要加快研发节奏',
    '产品委员会：要求优先考虑用户隐私和数据合规性',
    '机房突发状况：多台服务器宕机，资源需重新调配支持运维',
    '技术调研发现：在一个旧代码库中找到了类似问题的成熟解决方案',
    '研发小组提出了一个大胆的替代方案，令人耳目一新',
    '线上紧急Bug堆积，所有部门需抽调人手优先处理，导致本项目人手紧张',
    '业务方改变主意：基于最新市场调研，暗示了一个全新的产品方向',
    '突然收到了核心依赖库的重大版本更新通知，局面瞬间改变',
    '一场突发的全员会议让所有人不得不在下班前拿出结论',
]

# ── Session 管理 ──

_sessions: dict[str, dict] = {}


def create_session(topic: str, official_ids: list[str], task_id: str = '') -> dict:
    """创建新的朝堂议政会话。"""
    session_id = str(uuid.uuid4())[:8]

    officials = []
    for oid in official_ids:
        profile = OFFICIAL_PROFILES.get(oid)
        if profile:
            officials.append({**profile, 'id': oid})

    if not officials:
        return {'ok': False, 'error': '至少选择一位官员'}

    session = {
        'session_id': session_id,
        'topic': topic,
        'task_id': task_id,
        'officials': officials,
        'messages': [{
            'type': 'system',
            'content': f'🏛 部门站会开始 —— 议题：{topic}',
            'timestamp': time.time(),
        }],
        'round': 0,
        'phase': 'discussing',  # discussing | concluded
        'created_at': time.time(),
    }

    _sessions[session_id] = session
    return _serialize(session)


def advance_discussion(session_id: str, user_message: str = None,
                       decree: str = None) -> dict:
    """推进一轮讨论，使用内置模拟或 LLM。"""
    session = _sessions.get(session_id)
    if not session:
        return {'ok': False, 'error': f'会话 {session_id} 不存在'}

    session['round'] += 1
    round_num = session['round']

    # 记录业务方发言
    if user_message:
        session['messages'].append({
            'type': 'emperor',
            'content': user_message,
            'timestamp': time.time(),
        })

    # 记录突发事件
    if decree:
        session['messages'].append({
            'type': 'decree',
            'content': decree,
            'timestamp': time.time(),
        })

    # 尝试用 LLM 生成讨论
    llm_result = _llm_discuss(session, user_message, decree)

    if llm_result:
        new_messages = llm_result.get('messages', [])
        scene_note = llm_result.get('scene_note')
    else:
        # 降级到规则模拟
        new_messages = _simulated_discuss(session, user_message, decree)
        scene_note = None

    # 添加到历史
    for msg in new_messages:
        session['messages'].append({
            'type': 'official',
            'official_id': msg.get('official_id', ''),
            'official_name': msg.get('name', ''),
            'content': msg.get('content', ''),
            'emotion': msg.get('emotion', 'neutral'),
            'action': msg.get('action'),
            'timestamp': time.time(),
        })

    if scene_note:
        session['messages'].append({
            'type': 'scene_note',
            'content': scene_note,
            'timestamp': time.time(),
        })

    return {
        'ok': True,
        'session_id': session_id,
        'round': round_num,
        'new_messages': new_messages,
        'scene_note': scene_note,
        'total_messages': len(session['messages']),
    }


def get_session(session_id: str) -> dict | None:
    session = _sessions.get(session_id)
    if not session:
        return None
    return _serialize(session)


def conclude_session(session_id: str) -> dict:
    """结束议政，生成总结。"""
    session = _sessions.get(session_id)
    if not session:
        return {'ok': False, 'error': f'会话 {session_id} 不存在'}

    session['phase'] = 'concluded'

    # 尝试用 LLM 生成总结
    summary = _llm_summarize(session)
    if not summary:
        # 降级到简单统计
        official_msgs = [m for m in session['messages'] if m['type'] == 'official']
        by_name = {}
        for m in official_msgs:
            name = m.get('official_name', '?')
            by_name[name] = by_name.get(name, 0) + 1
        parts = [f"{n}发言{c}次" for n, c in by_name.items()]
        summary = f"历经{session['round']}轮讨论，{'、'.join(parts)}。议题待后续落实。"

    session['messages'].append({
        'type': 'system',
        'content': f'📋 部门站会结束 —— {summary}',
        'timestamp': time.time(),
    })
    session['summary'] = summary

    return {
        'ok': True,
        'session_id': session_id,
        'summary': summary,
    }


def list_sessions() -> list[dict]:
    """列出所有活跃会话。"""
    return [
        {
            'session_id': s['session_id'],
            'topic': s['topic'],
            'round': s['round'],
            'phase': s['phase'],
            'official_count': len(s['officials']),
            'message_count': len(s['messages']),
        }
        for s in _sessions.values()
    ]


def destroy_session(session_id: str):
    _sessions.pop(session_id, None)


def get_fate_event() -> str:
    """获取随机命运骰子事件。"""
    import random
    return random.choice(FATE_EVENTS)


# ── LLM 集成 ──

_PREFERRED_MODELS = ['gpt-4o-mini', 'claude-haiku', 'gpt-5-mini', 'gemini-3-flash', 'gemini-flash']

# GitHub Copilot 模型列表 (通过 Copilot Chat API 可用)
_COPILOT_MODELS = [
    'gpt-4o', 'gpt-4o-mini', 'claude-sonnet-4', 'claude-haiku-3.5',
    'gemini-2.0-flash', 'o3-mini',
]
_COPILOT_PREFERRED = ['gpt-4o-mini', 'claude-haiku', 'gemini-flash', 'gpt-4o']


def _pick_chat_model(models: list[dict]) -> str | None:
    """从 provider 的模型列表中选一个适合聊天的轻量模型。"""
    ids = [m['id'] for m in models if isinstance(m, dict) and 'id' in m]
    for pref in _PREFERRED_MODELS:
        for mid in ids:
            if pref in mid:
                return mid
    return ids[0] if ids else None


def _read_copilot_token() -> str | None:
    """读取 openclaw 管理的 GitHub Copilot token。"""
    token_path = os.path.expanduser('~/.openclaw/credentials/github-copilot.token.json')
    if not os.path.exists(token_path):
        return None
    try:
        with open(token_path) as f:
            cred = json.load(f)
        token = cred.get('token', '')
        expires = cred.get('expiresAt', 0)
        # 检查 token 是否过期（毫秒时间戳）
        import time
        if expires and time.time() * 1000 > expires:
            logger.warning('Copilot token expired')
            return None
        return token if token else None
    except Exception as e:
        logger.warning('Failed to read copilot token: %s', e)
        return None


def _get_llm_config() -> dict | None:
    """从 openclaw 配置读取 LLM 设置，支持环境变量覆盖。

    优先级: 环境变量 > github-copilot token > 本地 copilot-proxy > anthropic > 其他 provider
    """
    # 1. 环境变量覆盖（保留向后兼容）
    env_key = os.environ.get('OPENCLAW_LLM_API_KEY', '')
    if env_key:
        return {
            'api_key': env_key,
            'base_url': os.environ.get('OPENCLAW_LLM_BASE_URL', 'https://api.openai.com/v1'),
            'model': os.environ.get('OPENCLAW_LLM_MODEL', 'gpt-4o-mini'),
            'api_type': 'openai',
        }

    # 2. GitHub Copilot token（最优先 — 免费、稳定、无需额外配置）
    copilot_token = _read_copilot_token()
    if copilot_token:
        # 选一个 copilot 支持的模型
        model = 'gpt-4o'
        logger.info('Court discuss using github-copilot token, model=%s', model)
        return {
            'api_key': copilot_token,
            'base_url': 'https://api.githubcopilot.com',
            'model': model,
            'api_type': 'github-copilot',
        }

    # 3. 从 ~/.openclaw/openclaw.json 读取其他 provider 配置
    openclaw_cfg = os.path.expanduser('~/.openclaw/openclaw.json')
    if not os.path.exists(openclaw_cfg):
        return None

    try:
        with open(openclaw_cfg) as f:
            cfg = json.load(f)

        providers = cfg.get('models', {}).get('providers', {})

        # 按优先级排序：copilot-proxy > anthropic > 其他
        ordered = []
        for preferred in ['copilot-proxy', 'anthropic']:
            if preferred in providers:
                ordered.append(preferred)
        ordered.extend(k for k in providers if k not in ordered)

        for name in ordered:
            prov = providers.get(name)
            if not prov:
                continue
            api_type = prov.get('api', '')
            base_url = prov.get('baseUrl', '')
            api_key = prov.get('apiKey', '')
            if not base_url:
                continue

            # 跳过无 key 且非本地的 provider
            if not api_key or api_key == 'n/a':
                if 'localhost' not in base_url and '127.0.0.1' not in base_url:
                    continue

            model_id = _pick_chat_model(prov.get('models', []))
            if not model_id:
                continue

            # 本地代理先探测是否可用
            if 'localhost' in base_url or '127.0.0.1' in base_url:
                try:
                    import urllib.request
                    probe = urllib.request.Request(base_url.rstrip('/') + '/models', method='GET')
                    urllib.request.urlopen(probe, timeout=2)
                except Exception:
                    logger.info('Skipping provider=%s (not reachable)', name)
                    continue

            logger.info('Court discuss using openclaw provider=%s model=%s api=%s', name, model_id, api_type)
            send_auth = prov.get('authHeader', True) is not False and api_key not in ('', 'n/a')
            return {
                'api_key': api_key if send_auth else '',
                'base_url': base_url,
                'model': model_id,
                'api_type': api_type,
            }
    except Exception as e:
        logger.warning('Failed to read openclaw config: %s', e)

    return None


def _llm_complete(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> str | None:
    """调用 LLM API（自动适配 GitHub Copilot / OpenAI / Anthropic 协议）。"""
    config = _get_llm_config()
    if not config:
        return None

    import urllib.request
    import urllib.error

    api_type = config.get('api_type', 'openai-completions')

    if api_type == 'anthropic-messages':
        # Anthropic Messages API
        url = config['base_url'].rstrip('/') + '/v1/messages'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': config['api_key'],
            'anthropic-version': '2023-06-01',
        }
        payload = json.dumps({
            'model': config['model'],
            'system': system_prompt,
            'messages': [{'role': 'user', 'content': user_prompt}],
            'max_tokens': max_tokens,
            'temperature': 0.9,
        }).encode()
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return data['content'][0]['text']
        except Exception as e:
            logger.warning('Anthropic LLM call failed: %s', e)
            return None
    else:
        # OpenAI-compatible API (也适用于 github-copilot)
        if api_type == 'github-copilot':
            url = config['base_url'].rstrip('/') + '/chat/completions'
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {config['api_key']}",
                'Editor-Version': 'vscode/1.96.0',
                'Copilot-Integration-Id': 'vscode-chat',
            }
        else:
            url = config['base_url'].rstrip('/') + '/chat/completions'
            headers = {'Content-Type': 'application/json'}
            if config.get('api_key'):
                headers['Authorization'] = f"Bearer {config['api_key']}"
        payload = json.dumps({
            'model': config['model'],
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            'max_tokens': max_tokens,
            'temperature': 0.9,
        }).encode()
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode())
                return data['choices'][0]['message']['content']
        except Exception as e:
            logger.warning('LLM call failed: %s', e)
            return None


def _llm_discuss(session: dict, user_message: str = None, decree: str = None) -> dict | None:
    """使用 LLM 生成多官员讨论。"""
    officials = session['officials']
    names = '、'.join(o['name'] for o in officials)

    profiles = ''
    for o in officials:
        profiles += f"\n### {o['name']}（{o['role']}）\n"
        profiles += f"职责范围：{o.get('duty', '综合事务')}\n"
        profiles += f"性格：{o['personality']}\n"
        profiles += f"说话风格：{o['speaking_style']}\n"

    # 构建最近的对话历史
    history = ''
    for msg in session['messages'][-20:]:
        if msg['type'] == 'system':
            history += f"\n【系统】{msg['content']}\n"
        elif msg['type'] == 'emperor':
            history += f"\n业务方：{msg['content']}\n"
        elif msg['type'] == 'decree':
            history += f"\n【突发事件】{msg['content']}\n"
        elif msg['type'] == 'official':
            history += f"\n{msg.get('official_name', '?')}：{msg['content']}\n"
        elif msg['type'] == 'scene_note':
            history += f"\n（{msg['content']}）\n"

    if user_message:
        history += f"\n业务方：{user_message}\n"
    if decree:
        history += f"\n【突发事件——上帝视角干预】{decree}\n"

    decree_section = ''
    if decree:
        decree_section = '\n请根据突发事件改变讨论走向，所有成员都必须对此做出反应。\n'

    prompt = f"""你是一个技术部门多角色实时站会模拟器。模拟多位团队成员在会议上围绕议题的讨论。

## 参与成员
{names}

## 角色设定（每位成员都有明确的职责领域，必须从自身专业角度出发讨论）
{profiles}

## 当前议题
{session['topic']}

## 对话记录
{history if history else '（讨论刚刚开始）'}
{decree_section}
## 任务
生成每位成员的下一条发言。要求：
1. 每位成员说1-3句话，像真实技术会议讨论一样
2. **每位成员必须从自己的职责领域出发发言**——PMO谈进度和资源、产品谈需求和PRD、UI谈交互和视觉、前端谈页面和体验、后端谈接口和性能、测试谈质量和边界、运维谈部署和监控，每个人关注的焦点不同
3. 成员之间要有互动——回应、反驳、支持、补充，尤其是不同岗位的视角碰撞
4. 保持每位成员独特的说话风格和人格特征
5. 讨论要围绕议题推进、有实质性观点，不要泛泛而谈
6. 如果业务方发言了，成员要恰当回应
7. 可包含动作描写用*号*包裹

输出JSON格式：
{{
  "messages": [
    {{"official_id": "zhongshu", "name": "中书令", "content": "发言内容", "emotion": "neutral|confident|worried|angry|thinking|amused", "action": "可选动作描写"}},
    ...
  ],
  "scene_note": "可选的朝堂氛围变化（如：朝堂一片哗然|群臣窃窃私语），没有则为null"
}}

只输出JSON，不要其他内容。"""

    content = _llm_complete(
        '你是一个技术部门实时会议模拟器，严格输出JSON格式。',
        prompt,
        max_tokens=1500,
    )

    if not content:
        return None

    # 解析 JSON
    if '```json' in content:
        content = content.split('```json')[1].split('```')[0].strip()
    elif '```' in content:
        content = content.split('```')[1].split('```')[0].strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        logger.warning('Failed to parse LLM response: %s', content[:200])
        return None


def _llm_summarize(session: dict) -> str | None:
    """用 LLM 总结讨论结果。"""
    official_msgs = [m for m in session['messages'] if m['type'] == 'official']
    topic = session['topic']

    if not official_msgs:
        return None

    dialogue = '\n'.join(
        f"{m.get('official_name', '?')}：{m['content']}"
        for m in official_msgs[-30:]
    )

    prompt = f"""以下是技术部门各岗位成员围绕「{topic}」的讨论记录：

{dialogue}

请用2-3句话总结讨论结果、达成的共识和待办事项。使用专业且简明的风格。"""

    return _llm_complete('你是技术部门记录官，负责总结会议结果。', prompt, max_tokens=300)


# ── 规则模拟（无 LLM 时的降级方案）──

_SIMULATED_RESPONSES = {
    'pmo': [
        '我建议从项目全局出发，分三个阶段推进：先做需求调研，再输出方案，最后进入研发迭代。',
        '根据以往项目经验，建议先输出详细的项目计划，经评审后再正式启动。',
        '*查看进度表* 初始排期已拟好，待产品评审确认后即可分派任务。',
    ],
    'product': [
        '我发现当前方案在业务闭环上还存在风险，需要重新评估用户价值。',
        '坦白说，目前的PRD逻辑还不够完整，缺少了异常流程的处理。',
        '*分析竞品* 竞品最近上线了类似功能，我们必须在体验上做出差异化。',
    ],
    'ui': [
        '视觉层次上还需要再优化，目前的交互链路对用户来说太长了。',
        '建议统一使用设计系统中的标准组件，保证品牌一致性。',
        '*演示交互稿* 这里增加一个微动效，可以显著提升用户的操作反馈感。',
    ],
    'frontend': [
        '前端这边需要评估首屏加载性能，建议采用懒加载方案。',
        '状态管理逻辑比较复杂，我们需要先理清数据流向。',
        '*检查兼容性* 这个特性在旧版浏览器上可能有问题，建议做降级处理。',
    ],
    'backend': [
        '从架构稳定性考虑，高并发场景下的缓存穿透问题必须解决。',
        '数据库索引需要优化，否则大数据量下的查询性能会成为瓶颈。',
        '*查看接口文档* API定义需要保证幂等性，防止重复提交导致的数据异常。',
    ],
    'qa': [
        '测试用例需要覆盖更多的边界条件，目前只测了主流程。',
        '我建议增加一轮性能压测，确保系统能承载预期的QPS。',
        '*记录Bug* 这里的逻辑校验存在漏洞，如果不修复可能会导致安全风险。',
    ],
    'ops': [
        '运维这边建议建立灰度发布流程，出问题时能一键回滚。',
        '监控告警阈值需要重新设定，目前存在太多的无效告警。',
        '*检查资源* 生产环境的Pod副本数建议增加，以应对接下来的流量峰值。',
    ],
}

import random


def _simulated_discuss(session: dict, user_message: str = None, decree: str = None) -> list[dict]:
    """无 LLM 时的规则生成讨论内容。"""
    officials = session['officials']
    messages = []

    for o in officials:
        oid = o['id']
        pool = _SIMULATED_RESPONSES.get(oid, [])
        if isinstance(pool, set):
            pool = list(pool)
        if not pool:
            pool = ['臣附议。', '臣有不同看法。', '臣需要再想想。']

        content = random.choice(pool)
        emotions = ['neutral', 'confident', 'thinking', 'amused', 'worried']

        # 如果业务方发言了或有突发事件，调整回应
        if decree:
            content = f'*面露惊色* 突发事件，{content}'
        elif user_message:
            content = f'好的，{content}'

        messages.append({
            'official_id': oid,
            'name': o['name'],
            'content': content,
            'emotion': random.choice(emotions),
            'action': None,
        })

    return messages


def _serialize(session: dict) -> dict:
    return {
        'ok': True,
        'session_id': session['session_id'],
        'topic': session['topic'],
        'task_id': session.get('task_id', ''),
        'officials': session['officials'],
        'messages': session['messages'],
        'round': session['round'],
        'phase': session['phase'],
    }
