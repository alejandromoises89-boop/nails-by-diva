
export enum ServiceType {
  CAPPING = "💅 Capping Gel",
  MAINTENANCE = "✨ Mantenimiento",
  SEMIPERMANENT = "🎨 Semipermanente",
  SOFT_GEL = "💎 Soft Gel"
}

export enum PaymentMethod {
  CASH = "Efectivo",
  TRANSFER = "Transferencia",
  PIX = "Pix"
}

export enum AppointmentStatus {
  PENDING = "PENDIENTE",
  CONFIRMED = "CONFIRMADO",
  COMPLETED = "COMPLETADO"
}

export interface Appointment {
  id: string;
  clientName: string;
  date: string;
  time: string;
  service: ServiceType;
  paymentMethod: PaymentMethod;
  phone: string;
  status: AppointmentStatus;
  createdAt: number;
  amount?: number;
  paymentProof?: string;
  thankYouSent?: boolean;
}

export interface Expense {
  id: string;
  description: string;
  amount: number;
  date: string;
  category: string;
}

export interface AppSettings {
  paymentQr?: string;
}

export interface Review {
  id: string;
  clientName: string;
  rating: number;
  comment: string;
  date: string;
}

export interface CatalogItem {
  id: ServiceType;
  title: string;
  price: number;
  description: string;
  image: string;
}
