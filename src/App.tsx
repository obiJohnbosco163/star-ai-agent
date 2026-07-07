import { useEffect, useRef, useState } from 'react';
import starLogo from './assets/star-logo.png';
import backgroundAudio from './assets/yung_kai_-_blue_@BaseNaija.mp3';

const CROO_AGENT_URL = 'https://agent.croo.network/agents/888b2e91-245a-4776-b6aa-9e6fc1654a21';

const steps = [
  {
    title: 'Discover the signal',
    description: 'S.T.A.R. collects the context that matters so teams can understand the market, the company, and the right angle instantly.',
  },
  {
    title: 'Shape the approach',
    description: 'The agent turns research into crisp positioning, talking points, and a clear next-step narrative for outreach.',
  },
  {
    title: 'Launch with confidence',
    description: 'Every insight is packaged into a modern, action-ready experience that helps you move from idea to execution in minutes.',
  },
];

const highlights = ['Live on Croo Network', 'Modern AI workflow', 'Built for signal-driven outreach'];

function App() {
  const [soundOn, setSoundOn] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    if (!audioRef.current) {
      const audio = new Audio(backgroundAudio);
      audio.loop = true;
      audio.preload = 'auto';
      audio.volume = 0.35;
      audioRef.current = audio;
    }

    if (!soundOn) {
      audioRef.current.pause();
      return;
    }

    const playAudio = async () => {
      try {
        await audioRef.current?.play();
      } catch {
        // Ignore autoplay restrictions and let the user retry.
      }
    };

    void playAudio();

    return () => {
      audioRef.current?.pause();
    };
  }, [soundOn]);

  const handleUseAgent = () => {
    setSoundOn(true);

    if (typeof window !== 'undefined') {
      window.open(CROO_AGENT_URL, '_blank', 'noopener,noreferrer');
    }
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-slate-950 text-slate-100">
      <div className="aurora aurora-one" />
      <div className="aurora aurora-two" />
      <div className="mesh" />

      <div className="mx-auto flex min-h-screen max-w-7xl flex-col px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-8 flex items-center justify-between rounded-full border border-white/10 bg-white/10 px-4 py-3 shadow-[0_20px_80px_rgba(8,15,30,0.35)] backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full border border-cyan-400/40 bg-slate-900/80 shadow-[0_0_35px_rgba(45,212,191,0.25)]">
              <img src={starLogo} alt="S.T.A.R. logo" className="h-full w-full rounded-full object-cover" />
            </div>
            <div>
              <p className="text-[10px] uppercase tracking-[0.35em] text-cyan-300/80">AI agent • Croo Network</p>
              <h1 className="text-xl font-semibold tracking-tight text-white">S.T.A.R.</h1>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setSoundOn((value) => !value)}
            className="rounded-full border border-white/10 bg-slate-900/70 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-cyan-400/40 hover:text-white"
          >
            {soundOn ? 'Audio: On' : 'Audio: Off'}
          </button>
        </header>

        <main className="flex flex-1 flex-col justify-center">
          <div className="grid items-center gap-10 lg:grid-cols-[1.1fr_0.9fr]">
            <section className="animate-fade-up">
              <div className="mb-5 inline-flex items-center rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-sm font-medium text-cyan-300">
                Listed and online on Croo Network
              </div>

              <h2 className="max-w-3xl text-4xl font-semibold leading-tight sm:text-5xl lg:text-6xl">
                Meet the intelligence layer that turns prospect insight into momentum.
              </h2>

              <p className="mt-5 max-w-2xl text-lg text-slate-300 sm:text-xl">
                S.T.A.R. is a sleek AI agent that helps teams understand companies, shape smarter outreach, and move from research to action faster.
              </p>

              <div className="mt-8 flex flex-wrap gap-4">
                <a
                  href={CROO_AGENT_URL}
                  target="_blank"
                  rel="noreferrer"
                  onClick={handleUseAgent}
                  className="rounded-full bg-gradient-to-r from-cyan-400 to-violet-500 px-6 py-3 text-sm font-semibold text-slate-950 transition hover:scale-[1.02]"
                >
                  Use Agent
                </a>
                <button
                  type="button"
                  onClick={() => setSoundOn((value) => !value)}
                  className="rounded-full border border-white/10 bg-white/10 px-6 py-3 text-sm font-semibold text-slate-100 transition hover:border-cyan-400/40"
                >
                  {soundOn ? <>Ambient sound <span className="text-cyan-300">live</span></> : 'Turn on ambience'}
                </button>
              </div>

              <div className="mt-8 flex flex-wrap gap-3">
                {highlights.map((item) => (
                  <span
                    key={item}
                    className={`rounded-full border border-white/10 bg-slate-900/70 px-3 py-2 text-sm ${item.includes('Live') || item.includes('Croo Network') ? 'text-cyan-300' : 'text-slate-300'}`}
                  >
                    {item}
                  </span>
                ))}
              </div>
            </section>

            <section className="animate-float">
              <div className="rounded-[2rem] border border-white/10 bg-slate-900/70 p-6 shadow-[0_40px_140px_rgba(2,8,23,0.6)] backdrop-blur-2xl">
                <div className="rounded-[1.5rem] border border-cyan-400/20 bg-gradient-to-br from-cyan-400/10 via-slate-950 to-violet-500/10 p-6">
                  <div className="mb-6 flex items-center justify-between">
                    <div className="rounded-full border border-cyan-400/20 bg-slate-950/80 px-3 py-1 text-xs uppercase tracking-[0.3em] text-cyan-300">
                      Agent Experience
                    </div>
                    <div className="rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs uppercase tracking-[0.3em] text-cyan-300">
                      Live
                    </div>
                  </div>

                  <div className="flex items-center justify-center rounded-[1.75rem] border border-white/10 bg-slate-950/80 p-6">
                    <div className="h-36 w-36 overflow-hidden rounded-full shadow-[0_0_45px_rgba(34,211,238,0.17)]">
                      <img src={starLogo} alt="Star logo" className="h-full w-full rounded-full object-cover" />
                    </div>
                  </div>

                  <div className="mt-6 space-y-3 text-sm text-slate-300">
                    {['Research with context', 'Deliver crisp next steps', 'Launch with confidence'].map((item) => (
                      <div key={item} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </section>
          </div>

          <section className="mt-14">
            <div className="mb-6 flex items-end justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.35em] text-slate-400">How it works</p>
                <h3 className="mt-2 text-2xl font-semibold text-white">Three steps to make every conversation sharper.</h3>
              </div>
              <p className="hidden max-w-md text-sm text-slate-400 md:block">
                The agent combines <span className="text-cyan-300">live</span> context, structured insight, and deployment-ready guidance in one streamlined flow.
              </p>
            </div>

            <div className="grid gap-4 md:grid-cols-3">
              {steps.map((step, index) => (
                <article
                  key={step.title}
                  className="rounded-[1.4rem] border border-white/10 bg-white/5 p-6 shadow-[0_20px_70px_rgba(2,8,23,0.32)] backdrop-blur-xl transition hover:-translate-y-1 hover:border-cyan-400/30"
                >
                  <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 text-sm font-semibold text-slate-950">
                    0{index + 1}
                  </div>
                  <h4 className="text-lg font-semibold text-white">{step.title}</h4>
                  <p className="mt-3 text-sm leading-7 text-slate-300">{step.description}</p>
                </article>
              ))}
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
