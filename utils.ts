
import { Appointment } from './types';
import { BUSINESS_PHONE } from './constants';

export const generateId = () => Math.random().toString(36).substring(2, 8).toUpperCase();

export const formatCurrency = (amount: number) => 
  new Intl.NumberFormat('es-PY', { style: 'currency', currency: 'PYG', minimumFractionDigits: 0 }).format(amount);

export const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('es-ES', { weekday: 'long', day: 'numeric', month: 'long' }).format(date);
};

export const generateGoogleCalendarLink = (apt: Appointment) => {
  const dateStr = apt.date.replace(/-/g, '');
  const startTime = apt.time.replace(':', '') + '00';
  const [h, m] = apt.time.split(':');
  const endHour = (parseInt(h) + 1).toString().padStart(2, '0');
  const endTime = `${endHour}${m}00`;
  
  const title = encodeURIComponent(`Cita Nails by Diva: ${apt.service}`);
  const details = encodeURIComponent(`Turno #${apt.id} para ${apt.clientName}.\nServicio: ${apt.service}`);
  return `https://www.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dateStr}T${startTime}/${dateStr}T${endTime}&details=${details}`;
};

export const generateWhatsAppLink = (apt: Appointment, isReminder = false) => {
  const text = isReminder 
    ? `Hola ${apt.clientName}! Recordatorio de tu cita de ${apt.service} hoy a las ${apt.time}hs.`
    : `Hola Diva! Reserva #${apt.id}\nCliente: ${apt.clientName}\nServicio: ${apt.service}\nFecha: ${apt.date}\nHora: ${apt.time}hs\nPago: ${apt.paymentMethod}`;
  const phone = isReminder ? apt.phone : BUSINESS_PHONE;
  return `https://api.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(text)}`;
};

export const compressImage = (file: File): Promise<string> => {
  return new Promise((resolve) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (e) => {
      const img = new Image();
      img.src = e.target?.result as string;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = 600;
        canvas.height = (img.height * 600) / img.width;
        canvas.getContext('2d')?.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL('image/jpeg', 0.6));
      };
    };
  });
};
