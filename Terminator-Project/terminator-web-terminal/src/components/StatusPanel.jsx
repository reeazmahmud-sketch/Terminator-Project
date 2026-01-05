import React from 'react';
import { Activity, Users, MessageSquare, Clock, Bot } from 'lucide-react';

// Reusable metric bar component
const Metric = ({ icon: Icon, label, value, color = "bg-terminator-blue" }) => (
  <div className="flex flex-col gap-1 mb-4">
    <div className="flex justify-between items-center text-xs text-terminator-blue/80 font-mono">
      <div className="flex items-center gap-2">
        <Icon size={14} />
        {label}
      </div>
      <span>{value}%</span>
    </div>
    <div className="h-1.5 w-full bg-slate-800 rounded-full overflow-hidden">
      <div
        className={`h-full ${color} shadow-[0_0_10px_currentColor] transition-all duration-500`}
        style={{ width: `${value}%` }}
      ></div>
    </div>
  </div>
);

// Agent status badge (inline - too simple for separate file)
const AgentBadge = ({ name, messages, status }) => {
  const statusColor = {
    idle: 'bg-terminator-blue/10 border-terminator-blue/30',
    working: 'bg-terminator-glow/20 border-terminator-glow',
    error: 'bg-red-500/20 border-red-500/50',
    offline: 'bg-slate-700/30 border-slate-600'
  }[status] || 'bg-slate-700/30 border-slate-600';

  return (
    <div className={`flex justify-between items-center text-[10px] px-2 py-1.5 ${statusColor} border rounded font-mono`}>
      <span className="text-terminator-blue truncate max-w-[120px]">{name}</span>
      <span className="text-terminator-blue/60 ml-2">{messages}</span>
    </div>
  );
};

const StatusPanel = ({ metrics }) => {
  const { agents = [], system = {}, timestamp } = metrics;

  // Calculate percentages for visual bars
  const agentUtilization = system.agents_online > 0
    ? Math.round((system.agents_online / system.total_agents) * 100)
    : 0;

  const queueLoad = system.total_queue_size > 0
    ? Math.min(100, Math.round((system.total_queue_size / 50) * 100))
    : 0;

  return (
    <div className="h-2/3 bg-slate-900/50 backdrop-blur-md border border-terminator-blue/30 rounded-lg p-6 glow-border flex flex-col">
      <h3 className="text-terminator-blue font-display font-bold text-lg mb-6 border-b border-terminator-blue/20 pb-2">
        SYSTEM DIAGNOSTICS
      </h3>

      <div className="flex-1 overflow-y-auto pr-2">
        {/* System Metrics */}
        <Metric
          icon={Users}
          label="AGENT UTILIZATION"
          value={agentUtilization}
          color="bg-terminator-glow"
        />
        <Metric
          icon={MessageSquare}
          label="MESSAGE QUEUE"
          value={queueLoad}
          color={queueLoad > 75 ? "bg-red-500" : "bg-terminator-blue"}
        />

        {/* System Stats */}
        <div className="mt-6 p-3 bg-terminator-blue/5 rounded border border-terminator-blue/20">
          <div className="text-xs text-terminator-blue/60 font-mono mb-2">SYSTEM STATUS</div>
          <div className="grid grid-cols-2 gap-2 text-[10px] font-mono">
            <div className="text-terminator-blue/80">
              AGENTS: <span className="text-white">{system.agents_online}/{system.total_agents}</span>
            </div>
            <div className="text-terminator-blue/80">
              MESSAGES: <span className="text-white">{system.total_messages?.toLocaleString() || 0}</span>
            </div>
            <div className="text-terminator-blue/80">
              QUEUE: <span className="text-white">{system.total_queue_size || 0}</span>
            </div>
            <div className="text-terminator-blue/80 flex items-center gap-1">
              <Clock size={10} />
              <span className="text-white text-[9px]">{timestamp ? new Date(timestamp).toLocaleTimeString() : '--'}</span>
            </div>
          </div>
        </div>

        {/* Top Active Agents */}
        <div className="mt-4">
          <div className="text-xs text-terminator-blue/60 font-mono mb-2 flex items-center gap-2">
            <Bot size={12} className={agents.length > 0 ? "animate-pulse text-terminator-glow" : ""} />
            ACTIVE PROTOCOLS
          </div>
          <div className="flex flex-col gap-1.5 max-h-[200px] overflow-y-auto">
            {agents.length > 0 ? (
              agents.map(agent => (
                <AgentBadge
                  key={agent.name}
                  name={agent.name}
                  messages={agent.messages}
                  status={agent.status}
                />
              ))
            ) : (
              <div className="text-terminator-blue/40 text-[10px] italic">No active agents detected...</div>
            )}
          </div>
        </div>

        {/* Status Log (preserved) */}
        <div className="mt-4 font-mono text-[10px] text-terminator-blue/40 leading-relaxed">
          &gt; ESTABLISHING SECURE CONNECTION...<br/>
          &gt; AGENT BUS SYNCHRONIZED.<br/>
          &gt; REAL-TIME METRICS ENABLED.<br/>
          &gt; WELCOME, SIR.
        </div>
      </div>
    </div>
  );
};

export default StatusPanel;
