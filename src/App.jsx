import React, { useState, useEffect } from 'react';


function ProgressBar({ label, percent, detail }) {
  const bars = Math.round((percent / 100) * 20);
  const barString = '[' + '='.repeat(bars) + ' '.repeat(20 - bars) + ']';
  
  return (
    <div style={styles.metricRow}>
      <span style={styles.metricLabel}>{label}</span>
      <span style={styles.metricBar}>{barString} {percent.toFixed(1)}%</span>
      <span style={styles.metricDetail}>{detail}</span>
    </div>
  );
}

function App() {
  const [sys, setSys] = useState({ cpu: 0, ram: 0, disk: 0, uptime: 0, ram_used: 0, disk_used: 0 });
  const [doc, setDoc] = useState({ running: 0, total: 0, status: 'loading' });
  const [pih, setPih] = useState({ ratio: 0, ads_blocked: 0, domains: 0 });
  const [services, setServices] = useState([]);
  const [logs, setLogs] = useState(['> system init...', '> awaiting telemetry...']);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sysRes, docRes, pihRes, cfgRes] = await Promise.all([
          fetch('/api/system').catch(() => null),
          fetch('/api/docker').catch(() => null),
          fetch('/api/pihole').catch(() => null),
          fetch('/api/config').catch(() => null)
        ]);

        if (sysRes) setSys(await sysRes.json());
        if (docRes) setDoc(await docRes.json());
        if (pihRes) setPih(await pihRes.json());
        if (cfgRes) { const cfg = await cfgRes.json(); setServices(cfg.services); }
        
        setLogs(prev => {
          const newLogs = [...prev, `> telemetry synced [${new Date().toLocaleTimeString()}]`];
          return newLogs.slice(-4);
        });
      } catch (err) {
        setLogs(prev => [...prev.slice(-3), `> err: connection refused`]);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title} className="title-3d">HOMELAB</h1>
        <p style={styles.subtitle}>// COMMAND CENTER</p>
      </header>

      <div style={styles.monitorGrid}>
        <div className="box-3d" style={styles.monitorBox}>
          <h2 style={styles.monitorTitle}>[ SYSTEM NODE ]</h2>
          <ProgressBar label="CPU" percent={sys.cpu} detail={`${sys.uptime}h up`} />
          <ProgressBar label="RAM" percent={sys.ram} detail={`${sys.ram_used}GB`} />
          <ProgressBar label="DSK" percent={sys.disk} detail={`${sys.disk_used}GB`} />
        </div>

        <div className="box-3d" style={styles.monitorBox}>
          <h2 style={styles.monitorTitle}>[ DOCKER ENGINE ]</h2>
          <div style={styles.bigNumberBox}>
            <span style={styles.bigNumber}>{doc.running}</span>
            <span style={styles.bigLabel}>RUNNING / {doc.total} TOTAL</span>
          </div>
          <p style={styles.subText}>STATUS: {doc.status === 'online' ? 'CONNECTED' : 'OFFLINE/DENIED'}</p>
        </div>

        <div className="box-3d" style={styles.monitorBox}>
          <h2 style={styles.monitorTitle}>[ PI-HOLE DNS ]</h2>
          <div style={styles.bigNumberBox}>
            <span style={styles.bigNumber}>{pih.ratio}%</span>
            <span style={styles.bigLabel}>BLOCKED</span>
          </div>
          <p style={styles.subText}>{pih.ads_blocked.toLocaleString()} ADS | {pih.domains.toLocaleString()} RULES</p>
        </div>
      </div>

      <main style={styles.main}>
        <div style={styles.grid}>
          {services.map((service) => (
            <a key={service.id} href={service.url} target="_blank" rel="noreferrer" className="box-3d interactive" style={styles.card}>
              <div style={styles.cardHeader}>
                <span style={styles.serviceName}>{service.name}</span>
                <span style={styles.typeBadge}>{service.type}</span>
              </div>
              <div style={styles.cardDesc}>{service.desc}</div>
              <div style={styles.cardFooter}>
                <span style={styles.servicePort}>PORT:{service.port}</span>
                <div style={styles.cardStatus}>
                  <span style={styles.statusIndicator}></span>ONLINE
                </div>
              </div>
            </a>
          ))}
        </div>

        <div className="console-3d" style={styles.consoleBox}>
          {logs.map((log, i) => <div key={i} style={styles.logLine}>{log}</div>)}
          <div style={styles.logLine}><span style={styles.cursor}>_</span></div>
        </div>
      </main>
    </div>
  );
}

const styles = {
  container: { minHeight: '100vh', padding: '50px 20px', maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column' },
  header: { borderBottom: '4px solid #333', paddingBottom: '20px', marginBottom: '40px' },
  title: { fontSize: '64px', fontWeight: '900', color: '#FFFFFF', letterSpacing: '-3px', textTransform: 'uppercase' },
  subtitle: { fontSize: '16px', color: '#777777', marginTop: '8px', letterSpacing: '2px', fontFamily: 'monospace' },
  
  monitorGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px', marginBottom: '50px' },
  monitorBox: { padding: '24px', backgroundColor: '#000000' },
  monitorTitle: { color: '#FFFFFF', fontSize: '18px', marginBottom: '24px', letterSpacing: '2px', fontWeight: '900' },
  metricRow: { display: 'flex', justifyContent: 'space-between', marginBottom: '14px', fontSize: '14px', color: '#AAAAAA' },
  metricLabel: { width: '40px', fontWeight: 'bold', color: '#FFFFFF' },
  metricBar: { flex: 1, fontFamily: 'monospace', letterSpacing: '1px' },
  metricDetail: { width: '60px', textAlign: 'right' },
  bigNumberBox: { display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '12px' },
  bigNumber: { fontSize: '48px', fontWeight: '900', color: '#FFFFFF' },
  bigLabel: { fontSize: '14px', color: '#777777', letterSpacing: '1px', fontWeight: 'bold' },
  subText: { fontSize: '12px', color: '#555555', fontFamily: 'monospace' },

  main: { flex: 1 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '30px', marginBottom: '50px' },
  card: { display: 'flex', flexDirection: 'column', padding: '24px', textDecoration: 'none', color: 'inherit', cursor: 'pointer', backgroundColor: '#0A0A0A' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' },
  serviceName: { fontSize: '20px', fontWeight: '900', color: '#FFFFFF', letterSpacing: '1px' },
  typeBadge: { fontSize: '11px', color: '#000000', backgroundColor: '#FFFFFF', padding: '2px 8px', fontWeight: 'bold' },
  cardDesc: { fontSize: '12px', color: '#777777', marginBottom: '30px', lineHeight: '1.4' },
  cardFooter: { display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginTop: 'auto' },
  servicePort: { fontSize: '12px', color: '#555555', fontWeight: 'bold' },
  cardStatus: { fontSize: '12px', color: '#FFFFFF', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'bold' },
  statusIndicator: { width: '10px', height: '10px', backgroundColor: '#FFFFFF', display: 'inline-block' },
  
  consoleBox: { backgroundColor: '#000000', padding: '24px', color: '#777777', fontSize: '14px', lineHeight: '1.6' },
  logLine: { marginBottom: '6px' },
  cursor: { animation: 'blink 1s step-end infinite', color: '#FFFFFF', fontWeight: 'bold' }
};

export default App;
