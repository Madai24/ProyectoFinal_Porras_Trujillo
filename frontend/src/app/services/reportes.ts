import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { EstadisticasOut, ReporteOut } from '../models/huellas.models';

@Injectable({ providedIn: 'root' })
export class ReportesService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  listar(distritoId?: number, estadoId?: number, skip = 0, limit = 20): Observable<ReporteOut[]> {
    let params = new HttpParams().set('skip', skip).set('limit', limit);
    if (distritoId) params = params.set('distrito_id', distritoId);
    if (estadoId) params = params.set('estado_id', estadoId);
    return this.http.get<ReporteOut[]>(`${this.apiUrl}/reportes`, { params });
  }

  obtenerPorId(id: number): Observable<ReporteOut> {
    return this.http.get<ReporteOut>(`${this.apiUrl}/reportes/${id}`);
  }

  obtenerEstadisticas(): Observable<EstadisticasOut> {
    return this.http.get<EstadisticasOut>(`${this.apiUrl}/reportes/estadisticas`);
  }

  crear(formData: FormData): Observable<ReporteOut> {
    return this.http.post<ReporteOut>(`${this.apiUrl}/reportes`, formData);
  }

  actualizarEstado(id: number, estadoId: number): Observable<ReporteOut> {
    return this.http.patch<ReporteOut>(`${this.apiUrl}/reportes/${id}/estado`, { estado_id: estadoId });
  }

  eliminar(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/reportes/${id}`);
  }
}