import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import BookingForm from './components/BookingForm';
import AdminPanel from './components/AdminPanel';
import Confirmation from './components/Confirmation';
import ServiceCatalog from './components/ServiceCatalog';
import ReviewSection from './components/ReviewSection';
import { Appointment, AppointmentStatus, AppSettings, Expense, ServiceType, Review, ClientHistory } from './types';
import { STORAGE_KEY, SETTINGS_KEY, EXPENSES_KEY, REVIEWS_KEY, CLIENT_HISTORY_KEY } from './constants';
import { Sparkles, ShieldCheck, Home } from 'lucide-react';

const App: React.FC = () => {
  // State
  const [currentView, setCurrentView] = useState<'booking' | 'admin' | 'success'>('booking');
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [clientHistory, setClientHistory] = useState<ClientHistory>({});
  const [settings, setSettings] = useState<AppSettings>({});
  const [lastAppointment, setLastAppointment] = useState<Appointment | null>(null);
  const [preSelectedService, setPreSelectedService] = useState<ServiceType | undefined>(undefined);

  // Load from local storage on mount
  useEffect(() => {
    const storedData = localStorage.getItem(STORAGE_KEY);
    const storedSettings = localStorage.getItem(SETTINGS_KEY);
    const storedExpenses = localStorage.getItem(EXPENSES_KEY);
    const storedReviews = localStorage.getItem(REVIEWS_KEY);
    const storedHistory = localStorage.getItem(CLIENT_HISTORY_KEY);
    
    if (storedData) {
      try {
        setAppointments(JSON.parse(storedData));
      } catch (e) { console.error("Failed to parse appointments", e); }
    }
    
    if (storedSettings) {
      try {
        setSettings(JSON.parse(storedSettings));
      } catch (e) { console.error("Failed to parse settings", e); }
    }

    if (storedExpenses) {
        try {
          setExpenses(JSON.parse(storedExpenses));
        } catch (e) { console.error("Failed to parse expenses", e); }
    }

    if (storedReviews) {
        try {
          setReviews(JSON.parse(storedReviews));
        } catch (e) { console.error("Failed to parse reviews", e); }
    }

    if (storedHistory) {
      try {
        setClientHistory(JSON.parse(storedHistory));
      } catch (e) { console.error("Failed to parse client history", e); }
    }
  }, []);

  // Save to local storage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(appointments));
  }, [appointments]);

  useEffect(() => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    localStorage.setItem(EXPENSES_KEY, JSON.stringify(expenses));
  }, [expenses]);

  useEffect(() => {
    localStorage.setItem(REVIEWS_KEY, JSON.stringify(reviews));
  }, [reviews]);

  useEffect(() => {
    localStorage.setItem(CLIENT_HISTORY_KEY, JSON.stringify(clientHistory));
  }, [clientHistory]);

  // Handlers
  const handleBookingSuccess = (newApt: Appointment) => {
    setAppointments(prev => [...prev, newApt]);
    setLastAppointment(newApt);
    setCurrentView('success');
  };

  const handleUpdateStatus = (id: string, status: AppointmentStatus) => {
    setAppointments(prev => prev.map(apt => 
      apt.id === id ? { ...apt, status } : apt
    ));
  };

  const handleUpdateAmount = (id: string, amount: number) => {
    setAppointments(prev => prev.map(apt => 
      apt.id === id ? { ...apt, amount } : apt
    ));
  };

  const handleUpdateSettings = (newSettings: AppSettings) => {
    setSettings(newSettings);
  };

  const handleUploadProof = (id: string, proofBase64: string) => {
    setAppointments(prev => prev.map(apt => {
        if (apt.id === id) {
            const updated = { ...apt, paymentProof: proofBase64 };
            if (lastAppointment && lastAppointment.id === id) {
                setLastAppointment(updated);
            }
            return updated;
        }
        return apt;
    }));
  };

  const handleDelete = (id: string) => {
    if (confirm('¿Estás segura de borrar esta cita?')) {
      setAppointments(prev => prev.filter(apt => apt.id !== id));
    }
  };

  const handleAddExpense = (expense: Expense) => {
    setExpenses(prev => [...prev, expense]);
  };

  const handleDeleteExpense = (id: string) => {
    if (confirm('¿Borrar este gasto?')) {
        setExpenses(prev => prev.filter(e => e.id !== id));
    }
  };

  const handleAddReview = (review: Review) => {
    setReviews(prev => [review, ...prev]);
  };

  const handleMarkThankYouSent = (id: string, phone: string, quoteIndex: number) => {
    // 1. Mark appointment as sent
    setAppointments(prev => prev.map(apt => 
      apt.id === id ? { ...apt, thankYouSent: true } : apt
    ));

    // 2. Update client history
    setClientHistory(prev => {
      const currentHistory = prev[phone] || [];
      return {
        ...prev,
        [phone]: [...currentHistory, quoteIndex]
      };
    });
  };

  const handleSelectService = (service: ServiceType) => {
    setPreSelectedService(service);
    // Scroll to booking form
    const formElement = document.getElementById('booking-section');
    if (formElement) formElement.scrollIntoView({ behavior: 'smooth' });
  };

  const resetView = () => {
    setLastAppointment(null);
    setPreSelectedService(undefined);
    setCurrentView('booking');
  };

  return (
    <div className="min-h-screen bg-luxury-950 text-neutral-200 font-sans flex flex-col">
      <Header />

      <main className="flex-grow container mx-auto px-4 py-8 relative">
        {/* Decorative background elements */}
        <div className="fixed top-1/4 left-10 w-64 h-64 bg-gold-500/5 rounded-full blur-[100px] pointer-events-none"></div>
        <div className="fixed bottom-1/4 right-10 w-64 h-64 bg-purple-900/10 rounded-full blur-[100px] pointer-events-none"></div>

        {currentView === 'booking' && (
          <div className="animate-in fade-in duration-700 space-y-12">
            
            {/* 1. Catalog Section */}
            <ServiceCatalog onSelectService={handleSelectService} />
            
            {/* 2. Booking Form Section */}
            <div id="booking-section">
                <BookingForm 
                    onBookingSuccess={handleBookingSuccess} 
                    preSelectedService={preSelectedService}
                />
            </div>

            {/* 3. Review Section */}
            <ReviewSection reviews={reviews} onAddReview={handleAddReview} />
          </div>
        )}

        {currentView === 'success' && lastAppointment && (
          <Confirmation 
            appointment={lastAppointment} 
            onBack={resetView} 
            settings={settings}
            onUploadProof={handleUploadProof}
          />
        )}

        {currentView === 'admin' && (
          <div className="animate-in slide-in-from-bottom-5 duration-500">
            <AdminPanel 
              appointments={appointments} 
              settings={settings}
              expenses={expenses}
              clientHistory={clientHistory}
              onUpdateStatus={handleUpdateStatus} 
              onUpdateAmount={handleUpdateAmount}
              onUpdateSettings={handleUpdateSettings}
              onDelete={handleDelete} 
              onAddExpense={handleAddExpense}
              onDeleteExpense={handleDeleteExpense}
              onMarkThankYouSent={handleMarkThankYouSent}
            />
          </div>
        )}
      </main>

      <footer className="border-t border-neutral-900 bg-luxury-950 py-8 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p className="font-serif text-gold-500 text-lg mb-4">Nails by Diva</p>
          <div className="flex justify-center gap-6 mb-6">
            <button 
              onClick={() => setCurrentView('booking')}
              className={`text-xs uppercase tracking-widest hover:text-white transition-colors flex items-center gap-1 ${currentView === 'booking' ? 'text-white font-bold' : 'text-neutral-600'}`}
            >
              <Home className="w-3 h-3" /> Inicio
            </button>
            <button 
              onClick={() => setCurrentView('admin')}
              className={`text-xs uppercase tracking-widest hover:text-white transition-colors flex items-center gap-1 ${currentView === 'admin' ? 'text-white font-bold' : 'text-neutral-600'}`}
            >
              <ShieldCheck className="w-3 h-3" /> Admin
            </button>
          </div>
          <p className="text-neutral-700 text-xs">
            © {new Date().getFullYear()} All Rights Reserved. <br/> 
            <span className="opacity-50 flex items-center justify-center gap-1 mt-1">
              Made with <Sparkles className="w-2 h-2 text-gold-500" /> for luxury experiences.
            </span>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default App;