
import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import BookingForm from './components/BookingForm';
import AdminPanel from './components/AdminPanel';
import Confirmation from './components/Confirmation';
import ServiceCatalog from './components/ServiceCatalog';
import ReviewSection from './components/ReviewSection';
import { Appointment, AppSettings, Expense, ServiceType, Review, AppointmentStatus } from './types';
import { STORAGE_KEYS } from './constants';
import { Home, Shield } from 'lucide-react';

const App: React.FC = () => {
  const [view, setView] = useState<'booking' | 'admin' | 'success'>('booking');
  const [apps, setApps] = useState<Appointment[]>([]);
  const [exps, setExps] = useState<Expense[]>([]);
  const [sets, setSets] = useState<AppSettings>({});
  const [revs, setRevs] = useState<Review[]>([]);
  const [lastApp, setLastApp] = useState<Appointment | null>(null);
  const [selectedService, setSelectedService] = useState<ServiceType | undefined>(undefined);

  useEffect(() => {
    const a = localStorage.getItem(STORAGE_KEYS.APPOINTMENTS);
    const e = localStorage.getItem(STORAGE_KEYS.EXPENSES);
    const s = localStorage.getItem(STORAGE_KEYS.SETTINGS);
    const r = localStorage.getItem(STORAGE_KEYS.REVIEWS);
    if (a) setApps(JSON.parse(a));
    if (e) setExps(JSON.parse(e));
    if (s) setSets(JSON.parse(s));
    if (r) setRevs(JSON.parse(r));
  }, []);

  useEffect(() => localStorage.setItem(STORAGE_KEYS.APPOINTMENTS, JSON.stringify(apps)), [apps]);
  useEffect(() => localStorage.setItem(STORAGE_KEYS.EXPENSES, JSON.stringify(exps)), [exps]);
  useEffect(() => localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(sets)), [sets]);
  useEffect(() => localStorage.setItem(STORAGE_KEYS.REVIEWS, JSON.stringify(revs)), [revs]);

  const handleSelectService = (service: ServiceType) => {
    setSelectedService(service);
    document.getElementById('booking-form')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen flex flex-col bg-luxury-950 text-neutral-100">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        {view === 'booking' && (
          <div className="space-y-12 animate-in fade-in">
            <ServiceCatalog onSelectService={handleSelectService} />
            <div id="booking-form">
              <BookingForm 
                preSelectedService={selectedService} 
                onBookingSuccess={(a) => { setApps([...apps, a]); setLastApp(a); setView('success'); }} 
              />
            </div>
            <ReviewSection reviews={revs} onAddReview={(nr) => setRevs([...revs, nr])} />
          </div>
        )}
        {view === 'success' && lastApp && (
          <Confirmation 
            appointment={lastApp} 
            settings={sets} 
            onBack={() => { setView('booking'); setSelectedService(undefined); }} 
            onUploadProof={(id, p) => setApps(apps.map(a => a.id === id ? {...a, paymentProof: p} : a))} 
          />
        )}
        {view === 'admin' && (
          <AdminPanel 
            appointments={apps} 
            expenses={exps} 
            settings={sets} 
            onUpdateStatus={(id, s) => setApps(apps.map(a => a.id === id ? {...a, status: s} : a))} 
            onDelete={id => setApps(apps.filter(a => a.id !== id))} 
            onAddExpense={e => setExps([...exps, e])} 
            onUpdateSettings={setSets} 
          />
        )}
      </main>
      <footer className="p-8 border-t border-neutral-900 text-center flex justify-center gap-6">
        <button onClick={() => setView('booking')} className={`flex items-center gap-2 text-xs font-bold ${view === 'booking' ? 'text-gold-500' : 'text-neutral-500'}`}><Home className="w-3 h-3"/> Inicio</button>
        <button onClick={() => setView('admin')} className={`flex items-center gap-2 text-xs font-bold ${view === 'admin' ? 'text-gold-500' : 'text-neutral-500'}`}><Shield className="w-3 h-3"/> Admin</button>
      </footer>
    </div>
  );
};

export default App;
