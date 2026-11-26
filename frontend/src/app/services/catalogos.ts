import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Catalogo } from '../models/huellas.models';

@Injectable({ providedIn: 'root' })
export class CatalogosService {
  private http = inject(HttpClient);
  private apiUrl = 'http://127.0.0.1:8000';

  getDistritos(): Observable<Catalogo[]> {
    return this.http.get<Catalogo[]>(`${this.apiUrl}/distritos`);
  }

  getTiposResiduo(): Observable<Catalogo[]> {
    return this.http.get<Catalogo[]>(`${this.apiUrl}/tipos-residuo`);
  }

  getEstados(): Observable<Catalogo[]> {
    return this.http.get<Catalogo[]>(`${this.apiUrl}/estados`);
  }
}