import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { NotificacionesService } from '../../services/notificaciones';
import { mensajeError } from '../../utils/errores';

export const PASSWORD_MIN = 8;
export const PASSWORD_MAX = 128;

@Component({
  selector: 'app-registro',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './registro.html',
  styleUrl: './registro.css'
})
export class Registro {
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private notificaciones = inject(NotificacionesService);

  readonly passwordMin = PASSWORD_MIN;
  readonly passwordMax = PASSWORD_MAX;

  nombres = '';
  apellidos = '';
  correo = '';
  telefono = '';
  password = '';
  cargando = false;
  error = '';

  /** La contraseña cumple la regla del backend: de 8 a 128 caracteres. */
  get passwordLongitudOk(): boolean {
    return this.password.length >= PASSWORD_MIN && this.password.length <= PASSWORD_MAX;
  }

  /** Devuelve el primer problema del formulario, o '' si todo está bien. */
  private validar(): string {
    if (this.nombres.trim().length < 2) return 'Escribe tus nombres (mínimo 2 letras).';
    if (this.apellidos.trim().length < 2) return 'Escribe tus apellidos (mínimo 2 letras).';
    if (!this.correo.trim()) return 'Escribe tu correo electrónico.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.correo.trim())) {
      return 'El correo no tiene un formato válido. Ejemplo: nombre@correo.com';
    }
    if (this.telefono.trim().length > 15) return 'El teléfono no puede tener más de 15 caracteres.';
    if (!this.password) return 'Escribe una contraseña.';
    if (this.password.length < PASSWORD_MIN) {
      return `La contraseña es muy corta: tiene ${this.password.length} y necesita al menos ${PASSWORD_MIN} caracteres.`;
    }
    if (this.password.length > PASSWORD_MAX) {
      return `La contraseña es muy larga: el máximo es ${PASSWORD_MAX} caracteres.`;
    }
    return '';
  }

  registrar() {
    const problema = this.validar();
    if (problema) {
      this.error = problema;
      this.notificaciones.error(problema);
      return;
    }

    this.cargando = true;
    this.error = '';

    this.authService.registrar({
      nombres: this.nombres.trim(),
      apellidos: this.apellidos.trim(),
      correo: this.correo.trim(),
      password: this.password,
      telefono: this.telefono.trim() || null
    }).subscribe({
      next: () => {
        this.cargando = false;
        this.notificaciones.exito('¡Cuenta creada con éxito! Ahora inicia sesión.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = mensajeError(err, 'No se pudo crear la cuenta.');
        this.notificaciones.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }
}
