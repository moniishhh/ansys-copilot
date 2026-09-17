import { useState, useRef, useEffect, useLayoutEffect } from 'react'
import { createPortal } from 'react-dom'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Send, Copy, Check, Trash2, X, AlertCircle } from 'lucide-react'
import { FloatingPathsBackground } from './components/FloatingPathsBackground'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const MODES = [
  { id: 'chat',         label: 'General Q&A',    short: 'Ask'     },
  { id: 'apdl',         label: 'APDL Script',    short: 'APDL'    },
  { id: 'pymapdl',      label: 'PyMAPDL Script', short: 'PyMAPDL' },
  { id: 'troubleshoot', label: 'Troubleshoot',   short: 'Debug'   },
]

/* ── Copy button ───────────────────────────────────────── */
function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false)
  const handle = () => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  return (
    <button
      onClick={handle}
      style={{
        display: 'flex', alignItems: 'center', gap: 5,
        background: 'none', border: '1px solid rgba(255,255,255,0.15)',
        borderRadius: 6, padding: '4px 10px', cursor: 'pointer',
        color: copied ? '#fff' : 'rgba(255,255,255,0.4)',
        fontSize: 11, fontFamily: 'Inter', transition: 'all 0.15s',
      }}
    >
      {copied ? <Check size={11} /> : <Copy size={11} />}
      {copied ? 'COPIED' : 'COPY'}
    </button>
  )
}

/* ── Code block ────────────────────────────────────────── */
function CodeBlock({ code, language = 'python' }) {
  return (
    <div style={{ borderRadius: 14, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.08)', marginTop: 2 }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '8px 14px',
        background: 'rgba(255,255,255,0.04)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}>
        <span style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', fontFamily: 'Geist Mono, monospace', letterSpacing: '0.08em' }}>
          {language.toUpperCase()}
        </span>
        <CopyBtn text={code} />
      </div>
      <SyntaxHighlighter
        language={language === 'apdl' ? 'bash' : language}
        style={oneDark}
        customStyle={{
          margin: 0, padding: '16px 18px',
          background: 'rgba(8,4,2,0.8)',
          fontSize: 13, lineHeight: '1.65',
          fontFamily: 'Geist Mono, monospace',
        }}
      >
        {code}
      </SyntaxHighlighter>
    </div>
  )
}

/* ── Chat bubble ───────────────────────────────────────── */
function ChatMessage({ msg }) {
  const isUser = msg.role === 'user'

  if (isUser) {
    return (
      <div className="animate-slide-in" style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 24 }}>
        <div style={{
          maxWidth: '68%',
          background: 'rgba(255,255,255,0.07)',
          border: '1px solid rgba(255,255,255,0.11)',
          borderRadius: '18px 18px 4px 18px',
          padding: '13px 18px',
          fontSize: 14, lineHeight: 1.7,
          color: 'rgba(255,255,255,0.88)',
          fontWeight: 300,
        }}>
          {msg.content}
        </div>
      </div>
    )
  }

  return (
    <div className="animate-slide-in" style={{ display: 'flex', gap: 14, marginBottom: 28, alignItems: 'flex-start' }}>
      {/* Warm dot avatar */}
      <div style={{
        width: 9, height: 9, borderRadius: '50%', flexShrink: 0, marginTop: 7,
        background: 'radial-gradient(circle, #a855f7 0%, #7c3aed 100%)',
        boxShadow: '0 0 8px rgba(168,85,247,0.5)',
      }} />
      <div style={{ flex: 1, minWidth: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
        {msg.content && (
          <p style={{ fontSize: 14, lineHeight: 1.8, color: 'rgba(255,255,255,0.72)', fontWeight: 300, margin: 0, whiteSpace: 'pre-wrap' }}>
            {msg.content}
          </p>
        )}
        {msg.code && <CodeBlock code={msg.code} language={msg.language || 'python'} />}

        {/* Troubleshoot solutions */}
        {msg.solutions && (
          <div style={{ border: '1px solid rgba(255,255,255,0.08)', borderRadius: 14, overflow: 'hidden' }}>
            <div style={{ padding: '10px 16px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ fontSize: 11, letterSpacing: '0.1em', color: 'rgba(255,255,255,0.3)' }}>RECOMMENDED FIXES</span>
            </div>
            <div style={{ padding: '14px 16px', display: 'flex', flexDirection: 'column', gap: 12 }}>
              {msg.solutions.map((s, i) => (
                <div key={i} style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                  <span style={{ fontFamily: 'Geist Mono, monospace', fontSize: 11, color: 'rgba(168,85,247,0.7)', marginTop: 2, flexShrink: 0 }}>
                    {String(i + 1).padStart(2, '0')}
                  </span>
                  <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.65)', lineHeight: 1.65, fontWeight: 300 }}>{s}</span>
                </div>
              ))}
            </div>
            {msg.recommended_settings && (
              <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                <CodeBlock code={msg.recommended_settings} language="bash" />
              </div>
            )}
          </div>
        )}

        {msg.sources && msg.sources.filter(Boolean).length > 0 && (
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {msg.sources.filter(Boolean).slice(0, 4).map((src, i) => (
              <span key={i} style={{
                fontSize: 10, color: 'rgba(255,255,255,0.2)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 5, padding: '2px 8px',
                fontFamily: 'Geist Mono, monospace',
              }}>{src}</span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

/* ── Typing indicator ──────────────────────────────────── */
function TypingIndicator() {
  return (
    <div style={{ display: 'flex', gap: 14, alignItems: 'center', marginBottom: 28 }}>
      <div style={{
        width: 9, height: 9, borderRadius: '50%',
        background: 'radial-gradient(circle, #a855f7 0%, #7c3aed 100%)',
        boxShadow: '0 0 8px rgba(168,85,247,0.5)',
        flexShrink: 0,
      }} />
      <div style={{ display: 'flex', gap: 5 }}>
        {[0, 1, 2].map(i => (
          <div key={i} style={{
            width: 5, height: 5, borderRadius: '50%',
            background: 'rgba(168,85,247,0.6)',
            animation: `dot-bounce 1.3s ease-in-out ${i * 0.15}s infinite`,
          }} />
        ))}
      </div>
    </div>
  )
}

/* ── Welcome / empty state — Bolt-inspired premium layout ── */
function WelcomeState({ mode, onSuggest }) {
  const suggestions = {
    chat:         ['How do I set up a non-linear static analysis in ANSYS MAPDL?', 'Explain the difference between SOLID185 and SOLID186 elements', 'Best practices for meshing thin-walled pressure vessels'],
    apdl:         ['Steel cantilever beam under point load — APDL script', 'Modal analysis of a flat plate with fixed edges', 'Thermal analysis of a fin array'],
    pymapdl:      ['Static structural analysis of a pressure vessel', 'Fatigue life estimation using PyMAPDL', 'Buckling analysis of a slender column'],
    troubleshoot: ['Non-linear analysis not converging — excessive substep reductions', 'Element distortion warnings near curved geometry', 'Contact pairs not detecting in explicit dynamics'],
  }

  const modeColors = {
    chat:         { accent: 'rgba(168,85,247,0.8)',  glow: 'rgba(124,58,237,0.15)', dot: '#a855f7' },
    apdl:         { accent: 'rgba(168,85,247,0.8)',  glow: 'rgba(124,58,237,0.15)', dot: '#a855f7' },
    pymapdl:      { accent: 'rgba(168,85,247,0.8)',  glow: 'rgba(124,58,237,0.15)', dot: '#a855f7' },
    troubleshoot: { accent: 'rgba(168,85,247,0.8)',  glow: 'rgba(124,58,237,0.15)', dot: '#a855f7' },
  }
  const colors = modeColors[mode] || modeColors.chat

  return (
    <div style={{
      flex: 1,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      padding: '40px 24px', gap: 44,
      position: 'relative', overflow: 'hidden',
      minHeight: 0,
    }}>
      {/* Hero copy */}
      <div style={{ textAlign: 'center', maxWidth: 620, position: 'relative', zIndex: 1 }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '6px 16px',
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
          borderRadius: 99, marginBottom: 24,
          fontSize: 11, letterSpacing: '0.12em', color: 'rgba(255,255,255,0.3)',
        }}>
          <span style={{
            width: 6, height: 6, borderRadius: '50%',
            background: colors.dot,
            boxShadow: `0 0 8px ${colors.dot}`,
            display: 'inline-block',
          }} />
          {MODES.find(m => m.id === mode)?.label?.toUpperCase() || 'MODE'}
        </div>
        <h1 className="serif" style={{ fontSize: 52, color: '#fff', marginBottom: 16 }}>
          Your simulation intelligence,<br />ready to understand.
        </h1>
        <p style={{ fontSize: 15, color: 'rgba(255,255,255,0.38)', lineHeight: 1.75, fontWeight: 300 }}>
          Ask anything about ANSYS — generate APDL or PyMAPDL scripts,<br />
          diagnose convergence issues, and explore simulation strategies.
        </p>
      </div>

      {/* Suggestion chips — Bolt-style cards */}
      <div style={{ width: '100%', maxWidth: 580, position: 'relative', zIndex: 1 }}>
        <p style={{ fontSize: 10, letterSpacing: '0.14em', color: 'rgba(255,255,255,0.18)', textAlign: 'center', marginBottom: 12 }}>
          TRY ASKING
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 8 }}>
          {(suggestions[mode] || []).map((s, i) => (
            <button
              key={i}
              onClick={() => onSuggest(s)}
              style={{
                padding: '14px 20px',
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.07)',
                borderRadius: 14,
                fontSize: 13, color: 'rgba(255,255,255,0.45)',
                cursor: 'pointer', textAlign: 'left',
                fontFamily: 'Inter', fontWeight: 300, lineHeight: 1.5,
                transition: 'all 0.25s cubic-bezier(0.16,1,0.3,1)',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16,
              }}
              onMouseEnter={e => {
                e.currentTarget.style.borderColor = colors.accent.replace('0.8)', '0.35)')
                e.currentTarget.style.color = 'rgba(255,255,255,0.78)'
                e.currentTarget.style.background = colors.glow
                e.currentTarget.style.transform = 'translateY(-1px)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.3)'
              }}
              onMouseLeave={e => {
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.07)'
                e.currentTarget.style.color = 'rgba(255,255,255,0.45)'
                e.currentTarget.style.background = 'rgba(255,255,255,0.03)'
                e.currentTarget.style.transform = 'translateY(0)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              <span>{s}</span>
              <span style={{ fontSize: 16, opacity: 0.25, flexShrink: 0 }}>→</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

/* ── Top Navigation — logo + clear only (mode moved to input dropdown) ── */
function TopNav({ onClear, hasMessages }) {
  return (
    <nav style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 28px', height: 58,
      borderBottom: '1px solid rgba(255,255,255,0.07)',
      flexShrink: 0, position: 'relative', zIndex: 10,
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 9 }}>
        <svg width="22" height="14" viewBox="0 0 22 14" fill="none">
          <path d="M0 7L6 0L8 2L3.5 7L8 12L6 14L0 7Z" fill="white"/>
          <path d="M11 7L17 0L19 2L14.5 7L19 12L17 14L11 7Z" fill="white"/>
        </svg>
        <span style={{ fontSize: 14, fontWeight: 500, letterSpacing: '0.03em', color: '#fff' }}>
          ANSYS COPILOT
        </span>
      </div>

      {/* Right side */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {hasMessages && (
          <button
            onClick={onClear}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              padding: '7px 14px',
              background: 'none', border: '1px solid rgba(255,255,255,0.12)',
              borderRadius: 99, cursor: 'pointer',
              color: 'rgba(255,255,255,0.35)', fontSize: 11,
              letterSpacing: '0.08em', fontFamily: 'Inter',
              transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.35)' }}
            onMouseLeave={e => { e.currentTarget.style.color = 'rgba(255,255,255,0.35)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.12)' }}
          >
            <Trash2 size={10} />
            CLEAR
          </button>
        )}
        <div style={{
          padding: '8px 18px',
          background: '#fff', borderRadius: 99,
          fontSize: 11, fontWeight: 500, color: '#000',
          letterSpacing: '0.06em',
          display: 'flex', alignItems: 'center', gap: 6,
          userSelect: 'none',
        }}>
          ANSYS COPILOT
          <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
            <path d="M2 8L8 2M8 2H3M8 2V7" stroke="black" strokeWidth="1.5" strokeLinecap="round"/>
          </svg>
        </div>
      </div>
    </nav>
  )
}

/* ── Context fields — embedded inside InputBar ─────────── */
function ContextFields({ mode, extraFields, setExtraFields }) {
  const show = mode === 'troubleshoot' || mode === 'apdl' || mode === 'pymapdl'
  if (!show) return null

  const inputStyle = {
    flex: 1, minWidth: 160,
    background: 'rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.09)',
    borderRadius: 8, padding: '7px 12px',
    color: 'rgba(255,255,255,0.65)', fontSize: 12,
    fontFamily: 'Inter', outline: 'none', fontWeight: 300,
    transition: 'border-color 0.2s',
  }

  return (
    <div style={{
      display: 'flex', gap: 8, padding: '12px 16px 0',
      flexWrap: 'wrap', borderBottom: '1px solid rgba(255,255,255,0.06)',
      marginBottom: 2,
    }}>
      {(mode === 'apdl' || mode === 'pymapdl') && (
        <input
          placeholder="Analysis type (e.g. static structural)"
          value={extraFields.analysis_type}
          onChange={e => setExtraFields(f => ({ ...f, analysis_type: e.target.value }))}
          style={inputStyle}
          onFocus={e => e.target.style.borderColor = 'rgba(168,85,247,0.45)'}
          onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.09)'}
        />
      )}
      {mode === 'troubleshoot' && (
        <>
          <input placeholder="Error message (optional)" value={extraFields.error_message}
            onChange={e => setExtraFields(f => ({ ...f, error_message: e.target.value }))}
            style={inputStyle}
            onFocus={e => e.target.style.borderColor = 'rgba(168,85,247,0.45)'}
            onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.09)'}
          />
          <input placeholder="Current settings (optional)" value={extraFields.current_settings}
            onChange={e => setExtraFields(f => ({ ...f, current_settings: e.target.value }))}
            style={inputStyle}
            onFocus={e => e.target.style.borderColor = 'rgba(168,85,247,0.45)'}
            onBlur={e => e.target.style.borderColor = 'rgba(255,255,255,0.09)'}
          />
        </>
      )}
    </div>
  )
}

/* ── Mode dropdown — portal-rendered so it escapes all overflow/transform ancestors ─ */
function ModeDropdown({ mode, setMode }) {
  const [open, setOpen] = useState(false)
  const [rect, setRect] = useState(null)
  const btnRef = useRef(null)
  const current = MODES.find(m => m.id === mode) || MODES[0]

  const icons = {
    chat:         '💬',
    apdl:         '📄',
    pymapdl:      '🐍',
    troubleshoot: '🔧',
  }

  // Measure button position synchronously before the dropdown paints
  useLayoutEffect(() => {
    if (open && btnRef.current) {
      setRect(btnRef.current.getBoundingClientRect())
    }
  }, [open])

  // Close on scroll / resize
  useEffect(() => {
    if (!open) return
    const close = () => setOpen(false)
    window.addEventListener('scroll', close, true)
    window.addEventListener('resize', close)
    return () => {
      window.removeEventListener('scroll', close, true)
      window.removeEventListener('resize', close)
    }
  }, [open])

  const dropdown = rect && (
    <>
      {/* Backdrop */}
      <div
        style={{ position: 'fixed', inset: 0, zIndex: 9998 }}
        onClick={() => setOpen(false)}
      />
      {/* Panel — anchored to button's left edge, opens upward */}
      <div style={{
        position: 'fixed',
        left: rect.left,
        bottom: window.innerHeight - rect.top + 8,
        zIndex: 9999,
        minWidth: Math.max(rect.width, 210),
        background: 'rgba(12,6,20,0.98)',
        backdropFilter: 'blur(24px)',
        border: '1px solid rgba(168,85,247,0.25)',
        borderRadius: 14,
        boxShadow: '0 -8px 40px rgba(0,0,0,0.7), 0 0 0 1px rgba(255,255,255,0.04)',
        overflow: 'hidden',
        animation: 'fade-up 0.18s cubic-bezier(0.16,1,0.3,1) both',
      }}>
        <div style={{
          padding: '8px 14px 6px',
          fontSize: 10, letterSpacing: '0.12em',
          color: 'rgba(255,255,255,0.2)',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}>
          SELECT MODE
        </div>
        <div style={{ padding: '6px' }}>
          {MODES.map(m => {
            const active = mode === m.id
            return (
              <button
                key={m.id}
                onClick={() => { setMode(m.id); setOpen(false) }}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center', gap: 10,
                  padding: '9px 10px',
                  background: active ? 'rgba(168,85,247,0.12)' : 'none',
                  border: 'none', borderRadius: 9, cursor: 'pointer',
                  textAlign: 'left', transition: 'background 0.15s',
                }}
                onMouseEnter={e => { if (!active) e.currentTarget.style.background = 'rgba(255,255,255,0.04)' }}
                onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'none' }}
              >
                <span style={{ fontSize: 15, lineHeight: 1 }}>{icons[m.id]}</span>
                <div style={{ flex: 1 }}>
                  <div style={{
                    fontSize: 12, fontWeight: active ? 500 : 400,
                    color: active ? 'rgba(200,160,255,0.95)' : 'rgba(255,255,255,0.65)',
                    fontFamily: 'Inter', letterSpacing: '0.02em',
                  }}>{m.short}</div>
                  <div style={{
                    fontSize: 10, color: 'rgba(255,255,255,0.28)',
                    fontFamily: 'Inter', marginTop: 1,
                  }}>{m.label}</div>
                </div>
                {active && (
                  <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                    <path d="M2 6L5 9L10 3" stroke="#a855f7" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                )}
              </button>
            )
          })}
        </div>
      </div>
    </>
  )

  return (
    <div style={{ position: 'relative' }}>
      {/* Trigger pill */}
      <button
        ref={btnRef}
        onClick={() => setOpen(o => !o)}
        style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          padding: '5px 10px 5px 9px',
          background: open ? 'rgba(168,85,247,0.12)' : 'rgba(255,255,255,0.05)',
          border: `1px solid ${open ? 'rgba(168,85,247,0.4)' : 'rgba(255,255,255,0.09)'}`,
          borderRadius: 99, cursor: 'pointer',
          fontSize: 11, letterSpacing: '0.05em',
          color: open ? 'rgba(200,160,255,0.9)' : 'rgba(255,255,255,0.45)',
          fontFamily: 'Inter', fontWeight: 500,
          transition: 'all 0.18s ease',
          userSelect: 'none',
        }}
      >
        <span style={{
          width: 5, height: 5, borderRadius: '50%',
          background: '#a855f7',
          boxShadow: '0 0 6px #a855f7',
          display: 'inline-block', flexShrink: 0,
        }} />
        {current.short.toUpperCase()}
        <svg
          width="10" height="10" viewBox="0 0 10 10" fill="none"
          style={{ transition: 'transform 0.18s', transform: open ? 'rotate(180deg)' : 'rotate(0deg)', opacity: 0.5 }}
        >
          <path d="M2 3.5L5 6.5L8 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
        </svg>
      </button>

      {/* Portal-rendered dropdown */}
      {open && createPortal(dropdown, document.body)}
    </div>
  )
}

/* ── Input bar — Bolt-inspired premium redesign ─────────── */
function InputBar({ value, onChange, onSubmit, loading, mode, setMode, extraFields, setExtraFields }) {
  const ref = useRef(null)
  const [focused, setFocused] = useState(false)
  const [charCount, setCharCount] = useState(0)

  useEffect(() => {
    if (!ref.current) return
    ref.current.style.height = 'auto'
    ref.current.style.height = Math.min(ref.current.scrollHeight, 160) + 'px'
    setCharCount(value.length)
  }, [value])

  const placeholder = {
    chat:         'Ask anything about ANSYS simulation...',
    apdl:         'Describe the APDL script you need...',
    pymapdl:      'Describe the PyMAPDL script you need...',
    troubleshoot: 'Describe the problem you are facing...',
  }[mode] || 'Ask...'

  const canSend = value.trim() && !loading

  return (
    <div style={{ padding: '12px 28px 24px', flexShrink: 0, position: 'relative', zIndex: 10 }}>
      <div style={{ maxWidth: 760, margin: '0 auto' }}>

        {/* ── Outer glow wrapper */}
        <div style={{
          position: 'relative',
          borderRadius: 20,
          transition: 'box-shadow 0.3s ease',
          boxShadow: focused
            ? '0 0 0 1px rgba(168,85,247,0.4), 0 0 32px rgba(124,58,237,0.14), 0 8px 40px rgba(0,0,0,0.5)'
            : '0 0 0 1px rgba(255,255,255,0.09), 0 4px 24px rgba(0,0,0,0.4)',
        }}>

          {/* ── Inner card */}
          <div style={{
            borderRadius: 20,
            background: 'rgba(8,4,14,0.90)',
            backdropFilter: 'blur(20px)',
          }}>

            {/* Context fields embedded at top (for APDL / PyMAPDL / Troubleshoot) */}
            <ContextFields mode={mode} extraFields={extraFields} setExtraFields={setExtraFields} />

            {/* Textarea */}
            <div style={{ padding: '14px 16px 0' }}>
              <textarea
                ref={ref}
                rows={1}
                value={value}
                onChange={onChange}
                onFocus={() => setFocused(true)}
                onBlur={() => setFocused(false)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); onSubmit() } }}
                placeholder={placeholder}
                style={{
                  width: '100%', background: 'none', border: 'none', outline: 'none',
                  color: 'rgba(255,255,255,0.88)', fontSize: 14.5, lineHeight: '1.68',
                  fontFamily: 'Inter', fontWeight: 300, resize: 'none', overflowY: 'hidden',
                  minHeight: 52,
                }}
              />
            </div>

            {/* ── Bottom toolbar */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '10px 14px 12px',
            }}>
              {/* Left — mode dropdown + char count */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <ModeDropdown mode={mode} setMode={setMode} />

                {charCount > 0 && (
                  <span style={{
                    fontSize: 10, color: 'rgba(255,255,255,0.18)',
                    letterSpacing: '0.04em', fontFamily: 'Geist Mono, monospace',
                  }}>
                    {charCount}
                  </span>
                )}
              </div>

              {/* Right — keyboard hint + send button */}
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                {!loading && (
                  <span style={{
                    fontSize: 10, color: 'rgba(255,255,255,0.13)',
                    letterSpacing: '0.05em',
                  }}>
                    ⏎ SEND · ⇧⏎ NEW LINE
                  </span>
                )}

                <button
                  onClick={onSubmit}
                  disabled={!canSend}
                  style={{
                    height: 36, padding: '0 18px',
                    borderRadius: 99, flexShrink: 0,
                    background: canSend
                      ? 'linear-gradient(135deg, #a855f7 0%, #7c3aed 100%)'
                      : 'rgba(255,255,255,0.06)',
                    border: 'none', cursor: canSend ? 'pointer' : 'not-allowed',
                    display: 'flex', alignItems: 'center', gap: 7,
                    transition: 'all 0.2s cubic-bezier(0.16,1,0.3,1)',
                    fontSize: 11, fontWeight: 600, letterSpacing: '0.07em',
                    color: canSend ? '#fff' : 'rgba(255,255,255,0.2)',
                    fontFamily: 'Inter',
                    boxShadow: canSend ? '0 0 20px rgba(124,58,237,0.4), 0 2px 8px rgba(0,0,0,0.4)' : 'none',
                  }}
                  onMouseEnter={e => {
                    if (canSend) {
                      e.currentTarget.style.transform = 'scale(1.04)'
                      e.currentTarget.style.boxShadow = '0 0 28px rgba(168,85,247,0.55), 0 4px 12px rgba(0,0,0,0.4)'
                    }
                  }}
                  onMouseLeave={e => {
                    e.currentTarget.style.transform = 'scale(1)'
                    e.currentTarget.style.boxShadow = canSend ? '0 0 20px rgba(124,58,237,0.4), 0 2px 8px rgba(0,0,0,0.4)' : 'none'
                  }}
                  onMouseDown={e => { if (canSend) e.currentTarget.style.transform = 'scale(0.97)' }}
                  onMouseUp={e => { if (canSend) e.currentTarget.style.transform = 'scale(1.04)' }}
                >
                  {loading ? (
                    <>
                      <span style={{
                        width: 12, height: 12, borderRadius: '50%',
                        border: '2px solid rgba(255,255,255,0.3)',
                        borderTopColor: '#fff',
                        animation: 'spin 0.7s linear infinite',
                        display: 'inline-block',
                      }} />
                      THINKING
                    </>
                  ) : (
                    <>
                      SEND
                      <Send size={11} />
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Root ──────────────────────────────────────────────── */
export default function App() {
  const [mode, setMode] = useState('chat')
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [extraFields, setExtraFields] = useState({ analysis_type: '', error_message: '', current_settings: '' })
  const endRef = useRef(null)

  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, loading])

  const switchMode = m => {
    setMode(m); setMessages([]); setError(null)
    setExtraFields({ analysis_type: '', error_message: '', current_settings: '' })
  }

  const handleSubmit = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput(''); setError(null)
    setMessages(prev => [...prev, { role: 'user', content: text }])
    setLoading(true)
    try {
      if (mode === 'chat') {
        const res = await fetch(`${API_BASE}/chat`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text, conversation_history: messages.map(m => ({ role: m.role, content: m.content })) }),
        })
        if (!res.ok) throw new Error(`Server ${res.status}`)
        const d = await res.json()
        setMessages(p => [...p, { role: 'assistant', content: d.response, sources: d.sources }])
      } else if (mode === 'apdl' || mode === 'pymapdl') {
        const res = await fetch(`${API_BASE}/generate-script`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ description: text, script_type: mode, analysis_type: extraFields.analysis_type }),
        })
        if (!res.ok) throw new Error(`Server ${res.status}`)
        const d = await res.json()
        setMessages(p => [...p, { role: 'assistant', content: d.explanation, code: d.code, language: d.language }])
      } else {
        const res = await fetch(`${API_BASE}/troubleshoot`, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ problem: text, ...extraFields }),
        })
        if (!res.ok) throw new Error(`Server ${res.status}`)
        const d = await res.json()
        setMessages(p => [...p, { role: 'assistant', content: d.diagnosis, solutions: d.solutions, recommended_settings: d.recommended_settings }])
      }
    } catch (e) {
      setError(e.message || 'Could not reach the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <FloatingPathsBackground position={1} className="flex flex-col h-screen bg-black relative overflow-hidden">
      <TopNav onClear={() => { setMessages([]); setError(null) }} hasMessages={messages.length > 0} />

      {/* Messages area */}
      <div style={{ flex: 1, overflow: 'auto', position: 'relative', zIndex: 1 }}>
        {messages.length === 0
          ? <WelcomeState mode={mode} onSuggest={t => setInput(t)} />
          : (
            <div style={{ maxWidth: 740, margin: '0 auto', padding: '36px 28px' }}>
              {messages.map((m, i) => <ChatMessage key={i} msg={m} />)}
              {loading && <TypingIndicator />}
              <div ref={endRef} />
            </div>
          )
        }
      </div>

      {/* Error */}
      {error && (
        <div className="animate-fade-up" style={{
          position: 'fixed', bottom: 110, left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(10,3,0,0.95)', border: '1px solid rgba(220,60,30,0.35)',
          borderRadius: 12, padding: '11px 18px',
          display: 'flex', alignItems: 'center', gap: 10,
          fontSize: 12, color: 'rgba(255,130,80,0.9)',
          maxWidth: 480, zIndex: 100, fontFamily: 'Inter',
        }}>
          <AlertCircle size={14} />
          {error}
          <button onClick={() => setError(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'rgba(220,80,40,0.7)', padding: 2 }}>
            <X size={13} />
          </button>
        </div>
      )}

      <InputBar
        value={input}
        onChange={e => setInput(e.target.value)}
        onSubmit={handleSubmit}
        loading={loading}
        mode={mode}
        setMode={switchMode}
        extraFields={extraFields}
        setExtraFields={setExtraFields}
      />
    </FloatingPathsBackground>
  )
}
