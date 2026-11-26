import { Injectable, inject, PLATFORM_ID } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { isPlatformBrowser } from '@angular/common';
import { Observable, tap } from 'rxjs';
import { TokenResponse, UsuarioCreate, UsuarioOut } from '../models/huellas.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private http = inject(HttpClient);
  private platformId = inject(PLATFORM_ID);
  private apiUrl = 'http://127.0.0.1:8000';

  registrar(datos: UsuarioCreate): Observable<UsuarioOut> {
    return this.http.post<UsuarioOut>(`${this.apiUrl}/auth/registro`, datos);
  }

  login(email: string, password: string): Observable<TokenResponse> {
    const body = new HttpParams()
      .set('username', email)
      .set('password', password);

    const headers = new HttpHeaders({
      'Content-Type': 'application/x-www-form-urlencoded'
    });

    return this.http.post<TokenResponse>(`${this.apiUrl}/auth/login`, body.toString(), { headers }).pipe(
      tap((res) => {
        if (isPlatformBrowser(this.platformId)) {
          localStorage.setItem('huellas_token', res.access_token);
        }
      })
    );
  }

  obtenerPerfil(): Observable<UsuarioOut> {
    return this.http.get<UsuarioOut>(`${this.apiUrl}/usuarios/me`);
  }

  estaAutenticado(): boolean {
    if (isPlatformBrowser(this.platformId)) {
      return !!localStorage.getItem('huellas_token');
    }
    return false;
  }

  cerrarSesion(): void {
    if (isPlatformBrowser(this.platformId)) {
      localStorage.removeItem('huellas_token');
    }
  }
}