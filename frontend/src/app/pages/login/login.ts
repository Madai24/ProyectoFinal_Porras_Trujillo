import { Component, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

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

  email = '';
  password = '';
  cargando = false;
  error = '';

  iniciarSesion() {
    this.cargando = true;
    this.error = '';

    this.authService.login(this.email, this.password).subscribe({
      next: () => {
        this.cargando = false;
        this.cdr.detectChanges();
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.cargando = false;
        this.error = err.error?.detail || 'Correo o contraseña incorrectos.';
        this.cdr.detectChanges();
      }
    });
  }
}