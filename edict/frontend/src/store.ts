/**
 * Zustand Store — 三省六部看板状态管理
 * HTTP 5s 轮询，无 WebSocket
 */

import { create } from 'zustand';
import {
  api,
  type Task,
  type LiveStatus,
  type AgentConfig,
  type OfficialsData,
  type AgentsStatusData,
  type MorningBrief,
  type SubConfig,
  type ChangeLogEntry,
} from './api';

// ── Pipeline Definition (PIPE) ──

export const PIPE = [
  { key: 'Inbox',    dept: '业务方',   icon: '👤', action: '提需求' },
  { key: 'Backlog',  dept: 'PMO',     icon: '📋', action: '排期' },
  { key: 'Planning', dept: '产品',     icon: '💡', action: '规划' },
  { key: 'Designing',dept: 'UI',       icon: '🎨', action: '设计' },
  { key: 'Developing',dept: '研发',   icon: '💻', action: '开发' },
  { key: 'Testing',  dept: '测试',     icon: '🔍', action: '验证' },
  { key: 'ReadyForRelease', dept: '运维', icon: '🚀', action: '发布' },
  { key: 'Released', dept: '完成',     icon: '✅', action: '上线' },
] as const;

export const PIPE_STATE_IDX: Record<string, number> = {
  Inbox: 0, Pending: 0, Backlog: 1, Planning: 2, Designing: 3,
  Developing: 4, Testing: 5, ReadyForRelease: 6, Released: 7, Blocked: 4, Cancelled: 4, Done: 7,
};

export const DEPT_COLOR: Record<string, string> = {
  'PMO': '#e8a040', '产品': '#a07aff', 'UI': '#6a9eff', '前端': '#6aef9a',
  '后端': '#f5c842', '测试': '#ff9a6a', '运维': '#ff5270', '研发': '#44aaff',
  '业务方': '#ffd700', '完成': '#2ecc8a',
};

export const STATE_LABEL: Record<string, string> = {
  Inbox: '收件', Pending: '待处理', Backlog: '需求池', Planning: '产品规划',
  Designing: '设计中', Developing: '开发中', Testing: '测试联调', ReadyForRelease: '待发布',
  Released: '已上线', Done: '已完成', Blocked: '阻塞', Cancelled: '已取消',
};

export function deptColor(d: string): string {
  return DEPT_COLOR[d] || '#6a9eff';
}

export function stateLabel(t: Task): string {
  const r = t.review_round || 0;
  if (t.state === 'Testing' && r > 1) return `测试联调（第${r}轮）`;
  if (t.state === 'Developing' && r > 0) return `开发中（第${r}轮）`;
  return STATE_LABEL[t.state] || t.state;
}

export function isEdict(t: Task): boolean {
  return /^(JJC-|PRJ-)/i.test(t.id || '');
}

export function isSession(t: Task): boolean {
  return /^(OC-|MC-)/i.test(t.id || '');
}

export function isArchived(t: Task): boolean {
  return t.archived || ['Done', 'Released', 'Cancelled'].includes(t.state);
}

export type PipeStatus = { key: string; dept: string; icon: string; action: string; status: 'done' | 'active' | 'pending' };

export function getPipeStatus(t: Task): PipeStatus[] {
  const stateIdx = PIPE_STATE_IDX[t.state] ?? 4;
  return PIPE.map((stage, i) => ({
    ...stage,
    status: (i < stateIdx ? 'done' : i === stateIdx ? 'active' : 'pending') as 'done' | 'active' | 'pending',
  }));
}

// ── Tabs ──

export type TabKey =
  | 'edicts' | 'monitor' | 'officials' | 'models'
  | 'skills' | 'sessions' | 'memorials' | 'templates' | 'morning' | 'court';

export const TAB_DEFS: { key: TabKey; label: string; icon: string }[] = [
  { key: 'edicts',    label: '需求看板', icon: '📜' },
  { key: 'court',     label: '部门站会', icon: '🏛️' },
  { key: 'monitor',   label: '研发调度', icon: '🔌' },
  { key: 'officials', label: '人员总览', icon: '👔' },
  { key: 'models',    label: '模型配置', icon: '🤖' },
  { key: 'skills',    label: '技能配置', icon: '🎯' },
  { key: 'sessions',  label: '小任务',   icon: '💬' },
  { key: 'memorials', label: '项目归档', icon: '📦' },
  { key: 'templates', label: '需求库',   icon: '📋' },
  { key: 'morning',   label: '技术晨报', icon: '🌅' },
];

// ── DEPTS for monitor ──

export const DEPTS = [
  { id: 'pmo',      label: 'PMO',       emoji: '📋', role: '项目管理',  rank: 'P8' },
  { id: 'product',  label: '产品经理',  emoji: '💡', role: '产品经理',  rank: 'P7' },
  { id: 'ui',       label: 'UI设计师',  emoji: '🎨', role: 'UI设计师',  rank: 'P6' },
  { id: 'frontend', label: '前端工程师',emoji: '💻', role: '前端开发',  rank: 'P6' },
  { id: 'backend',  label: '后端工程师',emoji: '🗄️', role: '后端开发',  rank: 'P6' },
  { id: 'qa',       label: '测试工程师',emoji: '🔍', role: '质量保证',  rank: 'P6' },
  { id: 'ops',      label: '运维工程师',emoji: '🚀', role: '运维部署',  rank: 'P7' },
];

// ── Templates ──

export interface TemplateParam {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'select';
  default?: string;
  required?: boolean;
  options?: string[];
}

export interface Template {
  id: string;
  cat: string;
  icon: string;
  name: string;
  desc: string;
  depts: string[];
  est: string;
  cost: string;
  params: TemplateParam[];
  command: string;
}

export const TEMPLATES: Template[] = [
  {
    id: 'tpl-new-feature', cat: '产品需求', icon: '✨', name: '新增功能',
    desc: '规划并开发一个新的产品功能模块',
    depts: ['产品经理', '研发', '测试'], est: '~3天', cost: '¥5.0',
    params: [
      { key: 'feature_name', label: '功能名称', type: 'text', required: true },
      { key: 'target_users', label: '目标用户', type: 'text', default: '全部用户' },
      { key: 'core_value', label: '核心价值', type: 'textarea', default: '提升用户体验，增加转化率' },
    ],
    command: '请规划并开发【{feature_name}】功能，目标用户是【{target_users}】，核心价值是【{core_value}】。',
  },
  {
    id: 'tpl-bug-fix', cat: '研发维护', icon: '🐛', name: '紧急 Bug 修复',
    desc: '快速定位、修复并上线紧急缺陷',
    depts: ['研发', '测试', '运维'], est: '~2小时', cost: '¥1.0',
    params: [
      { key: 'bug_desc', label: 'Bug描述', type: 'textarea', required: true },
      { key: 'severity', label: '严重程度', type: 'select', options: ['P0-致命', 'P1-严重', 'P2-一般'], default: 'P1-严重' },
    ],
    command: '紧急修复线上【{severity}】Bug：【{bug_desc}】，请研发快速定位，测试验证后运维发版。',
  }
];

export const TPL_CATS = [
  { name: '全部', icon: '📋' },
  { name: '日常办公', icon: '💼' },
  { name: '数据分析', icon: '📊' },
  { name: '工程开发', icon: '⚙️' },
  { name: '内容创作', icon: '✍️' },
];

// ── Main Store ──

interface AppStore {
  // Data
  liveStatus: LiveStatus | null;
  agentConfig: AgentConfig | null;
  changeLog: ChangeLogEntry[];
  officialsData: OfficialsData | null;
  agentsStatusData: AgentsStatusData | null;
  morningBrief: MorningBrief | null;
  subConfig: SubConfig | null;

  // UI State
  activeTab: TabKey;
  edictFilter: 'active' | 'archived' | 'all';
  sessFilter: string;
  tplCatFilter: string;
  selectedOfficial: string | null;
  modalTaskId: string | null;
  countdown: number;

  // Toast
  toasts: { id: number; msg: string; type: 'ok' | 'err' }[];

  // Actions
  setActiveTab: (tab: TabKey) => void;
  setEdictFilter: (f: 'active' | 'archived' | 'all') => void;
  setSessFilter: (f: string) => void;
  setTplCatFilter: (f: string) => void;
  setSelectedOfficial: (id: string | null) => void;
  setModalTaskId: (id: string | null) => void;
  setCountdown: (n: number) => void;
  toast: (msg: string, type?: 'ok' | 'err') => void;

  // Data fetching
  loadLive: () => Promise<void>;
  loadAgentConfig: () => Promise<void>;
  loadOfficials: () => Promise<void>;
  loadAgentsStatus: () => Promise<void>;
  loadMorning: () => Promise<void>;
  loadSubConfig: () => Promise<void>;
  loadAll: () => Promise<void>;
}

let _toastId = 0;

export const useStore = create<AppStore>((set, get) => ({
  liveStatus: null,
  agentConfig: null,
  changeLog: [],
  officialsData: null,
  agentsStatusData: null,
  morningBrief: null,
  subConfig: null,

  activeTab: 'edicts',
  edictFilter: 'active',
  sessFilter: 'all',
  tplCatFilter: '全部',
  selectedOfficial: null,
  modalTaskId: null,
  countdown: 5,

  toasts: [],

  setActiveTab: (tab) => {
    set({ activeTab: tab });
    const s = get();
    if (['models', 'skills', 'sessions'].includes(tab) && !s.agentConfig) s.loadAgentConfig();
    if (tab === 'officials' && !s.officialsData) s.loadOfficials();
    if (tab === 'monitor') s.loadAgentsStatus();
    if (tab === 'morning' && !s.morningBrief) s.loadMorning();
  },
  setEdictFilter: (f) => set({ edictFilter: f }),
  setSessFilter: (f) => set({ sessFilter: f }),
  setTplCatFilter: (f) => set({ tplCatFilter: f }),
  setSelectedOfficial: (id) => set({ selectedOfficial: id }),
  setModalTaskId: (id) => set({ modalTaskId: id }),
  setCountdown: (n) => set({ countdown: n }),

  toast: (msg, type = 'ok') => {
    const id = ++_toastId;
    set((s) => ({ toasts: [...s.toasts, { id, msg, type }] }));
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
    }, 3000);
  },

  loadLive: async () => {
    try {
      const data = await api.liveStatus();
      set({ liveStatus: data });
      // Also preload officials for monitor tab
      const s = get();
      if (!s.officialsData) {
        api.officialsStats().then((d) => set({ officialsData: d })).catch(() => {});
      }
    } catch {
      // silently fail
    }
  },

  loadAgentConfig: async () => {
    try {
      const cfg = await api.agentConfig();
      const log = await api.modelChangeLog();
      set({ agentConfig: cfg, changeLog: log });
    } catch {
      // silently fail
    }
  },

  loadOfficials: async () => {
    try {
      const data = await api.officialsStats();
      set({ officialsData: data });
    } catch {
      // silently fail
    }
  },

  loadAgentsStatus: async () => {
    try {
      const data = await api.agentsStatus();
      set({ agentsStatusData: data });
    } catch {
      set({ agentsStatusData: null });
    }
  },

  loadMorning: async () => {
    try {
      const [brief, config] = await Promise.all([api.morningBrief(), api.morningConfig()]);
      set({ morningBrief: brief, subConfig: config });
    } catch {
      // silently fail
    }
  },

  loadSubConfig: async () => {
    try {
      const config = await api.morningConfig();
      set({ subConfig: config });
    } catch {
      // silently fail
    }
  },

  loadAll: async () => {
    const s = get();
    await s.loadLive();
    const tab = s.activeTab;
    if (['models', 'skills'].includes(tab)) await s.loadAgentConfig();
  },
}));

// ── Countdown & Polling ──

let _cdTimer: ReturnType<typeof setInterval> | null = null;

export function startPolling() {
  if (_cdTimer) return;
  useStore.getState().loadAll();
  _cdTimer = setInterval(() => {
    const s = useStore.getState();
    const cd = s.countdown - 1;
    if (cd <= 0) {
      s.setCountdown(5);
      s.loadAll();
    } else {
      s.setCountdown(cd);
    }
  }, 1000);
}

export function stopPolling() {
  if (_cdTimer) {
    clearInterval(_cdTimer);
    _cdTimer = null;
  }
}

// ── Utility ──

export function esc(s: string | undefined | null): string {
  if (!s) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function timeAgo(iso: string | undefined): string {
  if (!iso) return '';
  try {
    const d = new Date(iso.includes('T') ? iso : iso.replace(' ', 'T') + 'Z');
    if (isNaN(d.getTime())) return '';
    const diff = Date.now() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return '刚刚';
    if (mins < 60) return mins + '分钟前';
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return hrs + '小时前';
    return Math.floor(hrs / 24) + '天前';
  } catch {
    return '';
  }
}
