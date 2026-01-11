
import { ServiceType, PaymentMethod, CatalogItem } from './types';

export const BUSINESS_PHONE = "595992698406";
export const ADMIN_PIN = "2024";

export const SERVICES_LIST = Object.values(ServiceType);
export const PAYMENT_METHODS = Object.values(PaymentMethod);

export const BANKING_DETAILS = {
  FAMILIAR: { bank: "Banco Familiar", account: "815643114", label: "Nro. Cuenta" },
  UENO: { bank: "Ueno Bank", alias: "4437206", label: "Alias / C.I." }
};

export const CATALOG: Record<ServiceType, CatalogItem> = {
  [ServiceType.CAPPING]: {
    id: ServiceType.CAPPING,
    title: "Capping Gel",
    price: 120000,
    description: "Recubrimiento de gel sobre la uña natural para mayor resistencia.",
    image: "https://images.unsplash.com/photo-1604654894610-df63bc536371?auto=format&fit=crop&q=80&w=800"
  },
  [ServiceType.MAINTENANCE]: {
    id: ServiceType.MAINTENANCE,
    title: "Mantenimiento",
    price: 80000,
    description: "Relleno y corrección para mantener tus uñas impecables.",
    image: "https://images.unsplash.com/photo-1519014816548-bf5fe059e98b?auto=format&fit=crop&q=80&w=800"
  },
  [ServiceType.SEMIPERMANENT]: {
    id: ServiceType.SEMIPERMANENT,
    title: "Semipermanente",
    price: 70000,
    description: "Esmaltado de larga duración con curado en lámpara UV/LED.",
    image: "https://images.unsplash.com/photo-1632345031435-8727f6897d53?auto=format&fit=crop&q=80&w=800"
  },
  [ServiceType.SOFT_GEL]: {
    id: ServiceType.SOFT_GEL,
    title: "Soft Gel",
    price: 150000,
    description: "Extensión completa con tips de gel para un acabado natural.",
    image: "https://images.unsplash.com/photo-1522337360705-8754d1d7add9?auto=format&fit=crop&q=80&w=800"
  }
};

export const TIME_SLOTS: string[] = [];
for (let h = 8; h < 20; h++) {
  const hour = h.toString().padStart(2, '0');
  TIME_SLOTS.push(`${hour}:00`);
  TIME_SLOTS.push(`${hour}:30`);
}

export const STORAGE_KEYS = {
  APPOINTMENTS: 'diva_appointments',
  EXPENSES: 'diva_expenses',
  SETTINGS: 'diva_settings',
  REVIEWS: 'diva_reviews'
};
