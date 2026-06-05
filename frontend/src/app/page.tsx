'use client'

import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, TrendingUp, Target, Lightbulb, Zap, BarChart3, Users,
  MessageCircle, Sparkles, Rocket, Brain, Shield, Award, Play,
  Copy, Check, Loader2, AlertTriangle, Youtube, Crown, ArrowRight,
  RefreshCw, FileText, Compass, Gauge, Star, Flame, Hash,
} from 'lucide-react'

interface NicheAnalysis {
  niche: string
  market_overview: {
    trend_direction: string
    competition_level: string
    audience_demand: string
    difficulty: string
    growth_potential: string
    total_videos_analyzed: number
    total_channels_analyzed: number
    total_comments_analyzed: number
  }
  scores: {
    opportunity_score: number
    trend_score: number
    competition_score: number
    saturation_score: number
    demand_score: number
    monetization_score: number
    competition_inverse: number
    saturation_inverse: number
  }
  channel_prediction: {
    success_probability: {
      '1000_subscribers': number
      '10000_subscribers': number
      '100000_subscribers': number
      '1000000_subscribers': number
    }
    difficulty: string
    competition: string
    audience_demand: string
    growth_potential: string
    audience_size_estimate: string
    expected_publishing_frequency: string
    reasoning: string
  }
  trending_topics: Array<{ title: string; channel: string; views: number; published_at: string }>
  competitor_analysis: {
    top_competitors: Array<{ name: string; subscribers: number; growth_rate: number }>
    market_concentration: string
    content_strategy_insights: string[]
  }
  comment_intelligence: {
    total_comments_analyzed: number
    signals: {
      requests: { count: number; percentage: number }
      questions: { count: number; percentage: number }
      ideas: { count: number; percentage: number }
      pain_points: { count: number; percentage: number }
    }
    top_requests: string[]
    demand_signals: Array<{ text: string; count: number; urgency_score: number }>
  }
  ideas: {
    channel_ideas: Array<{ title: string; description: string; potential_score: number; source: string; reasoning: string }>
    video_ideas: Array<{ title: string; description: string; potential_score: number; source: string; reasoning: string; suggested_thumbnail?: string }>
    viral_opportunities: Array<{ title: string; description: string; potential_score: number; viral_potential: number; source: string; reasoning: string; suggested_thumbnail?: string }>
    underserved_niches: Array<{ title: string; description: string; gap_score: number; demand_count: number; existing_videos: number; reasoning: string }>
  }
}

const SUGGESTED_NICHES = [
  'AI Music', 'Football Songs', 'Gaming News', 'Personal Finance',
  'Crypto Education', 'Cooking', 'Motivation', 'History',
  'AI Technology', 'Self Improvement', 'Productivity', 'Comedy',
]

function ScoreGauge({ value, label, color = '#6366f1' }: { value: number; label: string; color?: string }) {
  const pct = Math.min((value / 100) * 100, 100)
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-20 h-20">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 36 36">
          <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(99,102,241,0.1)" strokeWidth="2.5" />
          <motion.circle cx="18" cy="18" r="15.5" fill="none" stroke={color} strokeWidth="2.5" strokeLinecap="round"
            strokeDasharray={`${pct} 100`} initial={{ strokeDasharray: '0 100' }} animate={{ strokeDasharray: `${pct} 100` }}
            transition={{ duration: 1.5, ease: 'easeOut' }} />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-lg font-bold" style={{ color }}>{value.toFixed(0)}</span>
        </div>
      </div>
      <span className="text-xs text-gray-400 text-center">{label}</span>
    </div>
  )
}

function ScoreBar({ value, label }: { value: number; label: string }) {
  const pct = Math.min((value / 100) * 100, 100)
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">{label}</span>
        <span className="text-white font-mono">{value.toFixed(1)}</span>
      </div>
      <div className="score-bar">
        <motion.div className="score-bar-fill" initial={{ width: 0 }} animate={{ width: `${pct}%` }}
          transition={{ duration: 1, ease: 'easeOut' }} />
      </div>
    </div>
  )
}

function Tag({ value, type }: { value: string; type?: string }) {
  const cls = type === 'low' ? 'tag tag-low' : type === 'medium' ? 'tag tag-medium' : type === 'high' ? 'tag tag-high' : 'tag bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
  return <span className={cls}>{value}</span>
}

function IdeaCard({ idea, index }: { idea: any; index: number }) {
  const [copied, setCopied] = useState(false)
  const score = idea.potential_score || idea.gap_score || 0
  return (
    <motion.div className="glass rounded-xl p-4 card-hover group" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}>
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-7 h-7 rounded-lg bg-indigo-500/10 flex items-center justify-center">
          <span className="text-xs font-bold text-indigo-400">#{index + 1}</span>
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-sm font-medium text-white line-clamp-2 group-hover:text-indigo-300 transition-colors">{idea.title}</h4>
            <div className="flex-shrink-0 flex items-center gap-1">
              <span className="text-xs font-mono font-bold" style={{ color: score > 80 ? '#34d399' : score > 60 ? '#fbbf24' : '#f87171' }}>{score.toFixed(0)}%</span>
              <button onClick={() => { navigator.clipboard.writeText(idea.title); setCopied(true); setTimeout(() => setCopied(false), 2000) }} className="p-1 rounded hover:bg-white/5">
                {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3 text-gray-500" />}
              </button>
            </div>
          </div>
          {idea.description && <p className="text-xs text-gray-500 mt-1 line-clamp-2">{idea.description}</p>}
          {idea.reasoning && <p className="text-xs text-gray-600 mt-1 italic line-clamp-2">{idea.reasoning}</p>}
          <div className="flex items-center gap-2 mt-2">
            <Tag value={idea.source?.replace(/_/g, ' ')} />
            {idea.viral_potential && <span className="text-xs text-pink-400">🔥 {idea.viral_potential.toFixed(0)}% viral</span>}
          </div>
        </div>
      </div>
    </motion.div>
  )
}

function LoadingSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass rounded-xl p-6">
            <div className="h-4 bg-indigo-500/5 rounded w-24 mb-3" />
            <div className="h-8 bg-indigo-500/10 rounded w-16 mb-2" />
            <div className="h-3 bg-indigo-500/5 rounded w-32" />
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="glass rounded-xl p-6">
            <div className="h-5 bg-indigo-500/5 rounded w-40 mb-4" />
            <div className="space-y-3">
              {[...Array(3)].map((_, j) => <div key={j} className="h-12 bg-indigo-500/5 rounded" />)}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function ParticleBackground() {
  return (
    <div className="particles">
      {Array.from({ length: 30 }, (_, i) => (
        <div key={i} className="particle" style={{
          left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%`,
          width: Math.random() * 3 + 1, height: Math.random() * 3 + 1,
          animationDelay: `${Math.random() * 20}s`, opacity: 0.3 + Math.random() * 0.4,
        }} />
      ))}
    </div>
  )
}

export default function Home() {
  const [niche, setNiche] = useState('')
  const [analysis, setAnalysis] = useState<NicheAnalysis | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const analyzeNiche = useCallback(async (n: string) => {
    if (!n.trim()) return
    setLoading(true); setError(null); setAnalysis(null)
    try {
      const res = await fetch(`/api/v1/niche/analyze/${encodeURIComponent(n.trim())}`)
      if (!res.ok) throw new Error(`API error: ${res.status}`)
      setAnalysis(await res.json())
    } catch (err: any) {
      setError(err.message || 'Failed to analyze niche')
    } finally { setLoading(false) }
  }, [])

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Compass },
    { id: 'scores', label: 'Scores', icon: Gauge },
    { id: 'trends', label: 'Trends', icon: TrendingUp },
    { id: 'ideas', label: 'Ideas', icon: Lightbulb },
    { id: 'viral', label: 'Viral', icon: Zap },
    { id: 'competitors', label: 'Competitors', icon: Users },
    { id: 'comments', label: 'Comments', icon: MessageCircle },
  ]

  return (
    <main className="relative min-h-screen">
      <ParticleBackground />

      {/* Header */}
      <header className="relative z-10 border-b border-indigo-500/10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <img src="/YTTH_logo.png" alt="YT Trend Hunter" className="w-10 h-10" />
              <div>
                <h1 className="text-xl font-bold gradient-text">YT Trend Hunter</h1>
                <p className="text-xs text-gray-500">AI-Powered Opportunity Discovery</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="hidden sm:flex items-center gap-1 text-xs text-gray-500">
                <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                API Connected
              </div>
              <a href="http://localhost:8000/docs" target="_blank" className="cyber-button cyber-button-secondary text-xs py-2 px-3">
                <FileText className="w-3 h-3" /> API
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative z-10 py-12 md:py-20">
        <div className="max-w-4xl mx-auto px-4 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-6">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <span className="text-sm text-indigo-300">AI-Powered YouTube Opportunity Discovery</span>
            </div>
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              Discover Opportunities <span className="gradient-text">Before</span><br />
              They Become Obvious
            </h1>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-8">
              Enter any niche and get instant AI-powered analysis of trends, competition,
              content gaps, and actionable ideas to grow your YouTube channel.
            </p>
          </motion.div>

          <motion.form onSubmit={(e) => { e.preventDefault(); analyzeNiche(niche) }} className="max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <div className="relative group">
              <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-pink-500 to-cyan-500 rounded-xl opacity-20 group-hover:opacity-30 blur transition duration-300" />
              <div className="relative flex items-center">
                <Search className="absolute left-4 w-5 h-5 text-gray-400" />
                <input type="text" value={niche} onChange={(e) => setNiche(e.target.value)}
                  placeholder="Enter a niche... (e.g., AI Music, Football Songs)"
                  className="cyber-input w-full pl-12 pr-36 py-4 rounded-xl text-lg" />
                <button type="submit" disabled={loading || !niche.trim()}
                  className="absolute right-2 cyber-button cyber-button-primary px-6 py-2.5 text-sm">
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Rocket className="w-4 h-4" /> Analyze</>}
                </button>
              </div>
            </div>
          </motion.form>

          <motion.div className="mt-6 flex flex-wrap justify-center gap-2" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}>
            <span className="text-xs text-gray-500 mr-1">Try:</span>
            {SUGGESTED_NICHES.slice(0, 8).map((n) => (
              <button key={n} onClick={() => { setNiche(n); analyzeNiche(n) }}
                className="text-xs px-3 py-1 rounded-full bg-indigo-500/5 border border-indigo-500/10 text-gray-400 hover:text-indigo-300 hover:border-indigo-500/30 transition-all">
                {n}
              </button>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Results */}
      <section className="relative z-10 pb-20">
        <div className="max-w-7xl mx-auto px-4">
          {error && (
            <motion.div className="glass rounded-xl p-6 border-red-500/20 mb-6" initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-red-400" />
                <p className="text-red-300">{error}</p>
              </div>
            </motion.div>
          )}

          {loading && <LoadingSkeleton />}

          <AnimatePresence mode="wait">
            {analysis && !loading && (
              <motion.div key={analysis.niche} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">

                {/* Niche Header */}
                <div className="glass rounded-2xl p-6 md:p-8 animated-border">
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-3 mb-2">
                        <h2 className="text-2xl md:text-3xl font-bold gradient-text">{analysis.niche}</h2>
                        <Tag value={analysis.market_overview.trend_direction} type={analysis.market_overview.trend_direction === 'growing' ? 'low' : 'medium'} />
                      </div>
                      <p className="text-gray-400">{analysis.market_overview.total_videos_analyzed} videos • {analysis.market_overview.total_comments_analyzed} comments analyzed</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <button onClick={() => { navigator.clipboard.writeText(JSON.stringify(analysis, null, 2)); setCopiedId('json'); setTimeout(() => setCopiedId(null), 2000) }}
                        className="cyber-button cyber-button-secondary text-xs py-2 px-3">
                        {copiedId === 'json' ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />} Export JSON
                      </button>
                      <button onClick={() => analyzeNiche(analysis.niche)} className="cyber-button cyber-button-secondary text-xs py-2 px-3">
                        <RefreshCw className="w-3 h-3" /> Refresh
                      </button>
                    </div>
                  </div>
                </div>

                {/* Tabs */}
                <div className="flex overflow-x-auto gap-1 pb-2">
                  {tabs.map((tab) => (
                    <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                      className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-indigo-500/15 text-indigo-300 border border-indigo-500/20' : 'text-gray-400 hover:text-gray-300 hover:bg-white/5'}`}>
                      <tab.icon className="w-4 h-4" /> {tab.label}
                    </button>
                  ))}
                </div>

                {/* Tab Content */}
                <AnimatePresence mode="wait">
                  {activeTab === 'overview' && (
                    <motion.div key="overview" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="space-y-6">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <motion.div className="stat-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <p className="text-sm text-gray-400">Opportunity Score</p>
                              <p className="text-2xl font-bold" style={{ color: '#6366f1' }}>{analysis.scores.opportunity_score.toFixed(1)}</p>
                              <p className="text-xs text-gray-500">Out of 100</p>
                            </div>
                            <div className="p-2 rounded-lg" style={{ background: '#6366f115' }}>
                              <TrendingUp className="w-5 h-5" style={{ color: '#6366f1' }} />
                            </div>
                          </div>
                        </motion.div>
                        <motion.div className="stat-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <p className="text-sm text-gray-400">Competition</p>
                              <p className="text-2xl font-bold" style={{ color: analysis.market_overview.competition_level === 'LOW' ? '#34d399' : '#fbbf24' }}>{analysis.market_overview.competition_level}</p>
                              <p className="text-xs text-gray-500">Inverse: {analysis.scores.competition_inverse.toFixed(0)}%</p>
                            </div>
                            <div className="p-2 rounded-lg" style={{ background: '#34d39915' }}>
                              <Shield className="w-5 h-5" style={{ color: '#34d399' }} />
                            </div>
                          </div>
                        </motion.div>
                        <motion.div className="stat-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <p className="text-sm text-gray-400">Difficulty</p>
                              <p className="text-2xl font-bold" style={{ color: '#f472b6' }}>{analysis.market_overview.difficulty}</p>
                              <p className="text-xs text-gray-500">{analysis.channel_prediction.reasoning.slice(0, 50)}...</p>
                            </div>
                            <div className="p-2 rounded-lg" style={{ background: '#f472b615' }}>
                              <Brain className="w-5 h-5" style={{ color: '#f472b6' }} />
                            </div>
                          </div>
                        </motion.div>
                        <motion.div className="stat-card" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
                          <div className="flex items-start justify-between">
                            <div className="space-y-1">
                              <p className="text-sm text-gray-400">Growth Potential</p>
                              <p className="text-2xl font-bold" style={{ color: '#06b6d4' }}>{analysis.market_overview.growth_potential}</p>
                              <p className="text-xs text-gray-500">Publish {analysis.channel_prediction.expected_publishing_frequency}</p>
                            </div>
                            <div className="p-2 rounded-lg" style={{ background: '#06b6d415' }}>
                              <Rocket className="w-5 h-5" style={{ color: '#06b6d4' }} />
                            </div>
                          </div>
                        </motion.div>
                      </div>

                      {/* Channel Prediction */}
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><Crown className="icon" /> Channel Creation Predictor</h3>
                        <p className="text-sm text-gray-400 mb-6">{analysis.channel_prediction.reasoning}</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                          {[
                            { label: '1K Subs', key: '1000_subscribers', value: analysis.channel_prediction.success_probability['1000_subscribers'] },
                            { label: '10K Subs', key: '10000_subscribers', value: analysis.channel_prediction.success_probability['10000_subscribers'] },
                            { label: '100K Subs', key: '100000_subscribers', value: analysis.channel_prediction.success_probability['100000_subscribers'] },
                            { label: '1M Subs', key: '1000000_subscribers', value: analysis.channel_prediction.success_probability['1000000_subscribers'] },
                          ].map((item) => (
                            <div key={item.key} className="text-center p-4 rounded-lg bg-indigo-500/5">
                              <div className="text-2xl md:text-3xl font-bold gradient-text-simple">{item.value.toFixed(1)}%</div>
                              <div className="text-xs text-gray-400 mt-1">{item.label}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Market + Competitor */}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="glass rounded-xl p-6">
                          <h3 className="section-title"><BarChart3 className="icon" /> Market Overview</h3>
                          <div className="space-y-4">
                            {[
                              { label: 'Trend Direction', value: analysis.market_overview.trend_direction },
                              { label: 'Competition Level', value: analysis.market_overview.competition_level },
                              { label: 'Audience Demand', value: analysis.market_overview.audience_demand },
                              { label: 'Difficulty', value: analysis.market_overview.difficulty },
                              { label: 'Growth Potential', value: analysis.market_overview.growth_potential },
                              { label: 'Audience Size', value: analysis.channel_prediction.audience_size_estimate },
                            ].map((item) => (
                              <div key={item.label} className="flex justify-between items-center">
                                <span className="text-sm text-gray-400">{item.label}</span>
                                <Tag value={item.value} type={item.value === 'LOW' || item.value === 'Very Easy' ? 'low' : item.value === 'MEDIUM' || item.value === 'Medium' ? 'medium' : 'high'} />
                              </div>
                            ))}
                          </div>
                        </div>
                        <div className="glass rounded-xl p-6">
                          <h3 className="section-title"><Target className="icon" /> Competitor Analysis</h3>
                          <div className="space-y-4">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-400">Market Concentration</span>
                              <Tag value={analysis.competitor_analysis.market_concentration} type="low" />
                            </div>
                            <div className="space-y-2">
                              <p className="text-sm text-gray-400">Insights:</p>
                              {analysis.competitor_analysis.content_strategy_insights.map((insight, i) => (
                                <div key={i} className="flex items-start gap-2 text-sm text-gray-300">
                                  <ArrowRight className="w-3 h-3 text-indigo-400 mt-1 flex-shrink-0" />
                                  <span>{insight}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'scores' && (
                    <motion.div key="scores" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><Gauge className="icon" /> Opportunity Scoring System</h3>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                          <ScoreGauge value={analysis.scores.opportunity_score} label="Opportunity" color="#6366f1" />
                          <ScoreGauge value={analysis.scores.trend_score} label="Trend" color="#06b6d4" />
                          <ScoreGauge value={analysis.scores.demand_score} label="Demand" color="#10b981" />
                          <ScoreGauge value={analysis.scores.monetization_score} label="Monetization" color="#f59e0b" />
                        </div>
                        <div className="space-y-3">
                          <ScoreBar value={analysis.scores.opportunity_score} label="Opportunity Score" />
                          <ScoreBar value={analysis.scores.trend_score} label="Trend Score" />
                          <ScoreBar value={analysis.scores.competition_inverse} label="Competition (Inverse)" />
                          <ScoreBar value={analysis.scores.saturation_inverse} label="Saturation (Inverse)" />
                          <ScoreBar value={analysis.scores.demand_score} label="Audience Demand" />
                          <ScoreBar value={analysis.scores.monetization_score} label="Monetization Potential" />
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'trends' && (
                    <motion.div key="trends" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><TrendingUp className="icon" /> Trending Topics <span className="text-xs text-gray-500 font-normal ml-2">({analysis.trending_topics.length} found)</span></h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {analysis.trending_topics.map((topic, i) => (
                            <motion.div key={i} className="glass rounded-lg p-4 card-hover" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                              <div className="flex items-start gap-3">
                                <div className="flex-shrink-0 w-6 h-6 rounded bg-indigo-500/10 flex items-center justify-center">
                                  <span className="text-xs font-bold text-indigo-400">{i + 1}</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                  <p className="text-sm text-white line-clamp-2">{topic.title}</p>
                                  <div className="flex items-center gap-3 mt-1">
                                    <span className="text-xs text-gray-500">{topic.channel}</span>
                                    <span className="text-xs text-gray-600">•</span>
                                    <span className="text-xs text-gray-500">{new Date(topic.published_at).toLocaleDateString()}</span>
                                  </div>
                                </div>
                              </div>
                            </motion.div>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'ideas' && (
                    <motion.div key="ideas" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div className="glass rounded-xl p-6">
                          <h3 className="section-title"><Lightbulb className="icon" /> Channel Ideas <span className="text-xs text-gray-500 font-normal ml-2">({analysis.ideas.channel_ideas.length})</span></h3>
                          <div className="space-y-3">
                            {analysis.ideas.channel_ideas.map((idea, i) => <IdeaCard key={i} idea={idea} index={i} />)}
                            {analysis.ideas.channel_ideas.length === 0 && <p className="text-sm text-gray-500 text-center py-8">No channel ideas generated yet.</p>}
                          </div>
                        </div>
                        <div className="glass rounded-xl p-6">
                          <h3 className="section-title"><Play className="icon" /> Video Ideas <span className="text-xs text-gray-500 font-normal ml-2">({analysis.ideas.video_ideas.length})</span></h3>
                          <div className="space-y-3">
                            {analysis.ideas.video_ideas.map((idea, i) => <IdeaCard key={i} idea={idea} index={i} />)}
                            {analysis.ideas.video_ideas.length === 0 && <p className="text-sm text-gray-500 text-center py-8">No video ideas generated yet.</p>}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'viral' && (
                    <motion.div key="viral" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><Zap className="icon" /> Viral Opportunities <span className="text-xs text-gray-500 font-normal ml-2">({analysis.ideas.viral_opportunities.length})</span></h3>
                        <div className="space-y-3">
                          {analysis.ideas.viral_opportunities.map((idea, i) => <IdeaCard key={i} idea={idea} index={i} />)}
                          {analysis.ideas.viral_opportunities.length === 0 && <p className="text-sm text-gray-500 text-center py-8">No viral opportunities detected.</p>}
                        </div>
                      </div>
                      {analysis.ideas.underserved_niches.length > 0 && (
                        <div className="glass rounded-xl p-6 mt-6">
                          <h3 className="section-title"><Star className="icon" /> Underserved Niches <span className="text-xs text-gray-500 font-normal ml-2">({analysis.ideas.underserved_niches.length})</span></h3>
                          <div className="space-y-3">
                            {analysis.ideas.underserved_niches.map((niche, i) => <IdeaCard key={i} idea={niche} index={i} />)}
                          </div>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'competitors' && (
                    <motion.div key="competitors" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><Users className="icon" /> Competitor Analysis</h3>
                        <div className="space-y-4">
                          <div className="flex justify-between items-center">
                            <span className="text-sm text-gray-400">Market Concentration</span>
                            <Tag value={analysis.competitor_analysis.market_concentration} type="low" />
                          </div>
                          <div className="space-y-2">
                            <p className="text-sm text-gray-400">Strategy Insights:</p>
                            {analysis.competitor_analysis.content_strategy_insights.map((insight, i) => (
                              <div key={i} className="flex items-start gap-2 text-sm text-gray-300 p-3 rounded-lg bg-indigo-500/5">
                                <ArrowRight className="w-3 h-3 text-indigo-400 mt-1 flex-shrink-0" />
                                <span>{insight}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'comments' && (
                    <motion.div key="comments" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                      <div className="glass rounded-xl p-6">
                        <h3 className="section-title"><MessageCircle className="icon" /> Comment Intelligence</h3>
                        <p className="text-sm text-gray-400 mb-6">{analysis.comment_intelligence.total_comments_analyzed} comments analyzed</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                          {[
                            { label: 'Requests', value: analysis.comment_intelligence.signals.requests.count, pct: analysis.comment_intelligence.signals.requests.percentage },
                            { label: 'Questions', value: analysis.comment_intelligence.signals.questions.count, pct: analysis.comment_intelligence.signals.questions.percentage },
                            { label: 'Ideas', value: analysis.comment_intelligence.signals.ideas.count, pct: analysis.comment_intelligence.signals.ideas.percentage },
                            { label: 'Pain Points', value: analysis.comment_intelligence.signals.pain_points.count, pct: analysis.comment_intelligence.signals.pain_points.percentage },
                          ].map((item) => (
                            <div key={item.label} className="text-center p-4 rounded-lg bg-indigo-500/5">
                              <div className="text-2xl font-bold gradient-text-simple">{item.value}</div>
                              <div className="text-xs text-gray-400 mt-1">{item.label}</div>
                              <div className="text-xs text-gray-500">{item.pct.toFixed(1)}%</div>
                            </div>
                          ))}
                        </div>
                        {analysis.comment_intelligence.top_requests.length > 0 && (
                          <div>
                            <p className="text-sm text-gray-400 mb-3">Top Requests:</p>
                            <div className="space-y-2">
                              {analysis.comment_intelligence.top_requests.map((req, i) => (
                                <div key={i} className="flex items-start gap-2 text-sm text-gray-300 p-2 rounded bg-indigo-500/5">
                                  <Hash className="w-3 h-3 text-indigo-400 mt-1 flex-shrink-0" />
                                  <span>{req}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-indigo-500/10 py-8">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-sm text-gray-500">
            Built with ❤️ by <span className="gradient-text-simple">0xNullDev</span> — AI-Powered YouTube Opportunity Discovery
          </p>
        </div>
      </footer>
    </main>
  )
}
