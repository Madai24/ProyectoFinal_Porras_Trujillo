import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

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

  nombre_completo = '';
  email = '';
  password = '';
  cargando = false;
  error = '';

  registrar() {
    this.cargando = true;
    this.error = '';

    this.authService.registrar({
      nombre_completo: this.nombre_completo,
      email: this.email,
      password: this.password
    }).subscribe({
      next: () => {
        this.cargando = false;
        this.cdr.detectChanges();
        alert('¡Cuenta creada con éxito! Ahora inicia sesión.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'No se pudo completar el registro. Verifica tus datos.';
        this.cdr.detectChanges();
      }
    });
  }
}