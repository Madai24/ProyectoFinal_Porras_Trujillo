import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';
import { NotificacionesService } from '../../services/notificaciones';
import { mensajeError } from '../../utils/errores';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  private authService = inject(AuthService);
  private router = inject(Router);
  private cdr = inject(ChangeDetectorRef);
  private notificaciones = inject(NotificacionesService);

  email = '';
  password = '';
  cargando = false;
  error = '';

  iniciarSesion() {
    if (!this.email.trim() || !this.password) {
      this.error = 'Escribe tu correo y tu contraseña.';
      this.notificaciones.error(this.error);
      return;
    }

    this.cargando = true;
    this.error = '';

    this.authService.login(this.email.trim(), this.password).subscribe({
      next: () => {
        this.cargando = false;
        this.notificaciones.exito('¡Bienvenido/a! Sesión iniciada.');
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.status === 401
          ? 'Correo o contraseña incorrectos. Revisa tus datos o crea una cuenta.'
          : mensajeError(err, 'No se pudo iniciar sesión.');
        this.notificaciones.error(this.error);
        this.cdr.detectChanges();
      }
    });
  }
}