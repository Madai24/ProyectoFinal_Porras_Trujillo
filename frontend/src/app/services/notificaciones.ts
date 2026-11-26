import { Injectable, signal } from '@angular/core';

export type TipoAviso = 'exito' | 'error' | 'info';

export interface Aviso {
  id: number;
  tipo: TipoAviso;
  texto: string;
}

/** Avisos flotantes (toasts) para informar al usuario si algo salió bien o mal. */
@Injectable({ providedIn: 'root' })
export class NotificacionesService {
  private siguienteId = 0;
  readonly avisos = signal<Aviso[]>([]);

  exito(texto: string): void {
    this.mostrar('exito', texto, 4000);
  }

  error(texto: string): void {
    this.mostrar('error', texto, 8000);
  }

  info(texto: string): void {
    this.mostrar('info', texto, 4000);
  }

  cerrar(id: number): void {
    this.avisos.update((lista) => lista.filter((a) => a.id !== id));
  }

  private mostrar(tipo: TipoAviso, texto: string, duracionMs: number): void {
    const id = ++this.siguienteId;
    this.avisos.update((lista) => [...lista, { id, tipo, texto }]);
    setTimeout(() => this.cerrar(id), duracionMs);
  }
}
