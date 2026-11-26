import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../services/auth';
import { UsuarioOut } from '../../models/huellas.models';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './perfil.html',
  styleUrl: './perfil.css'
})
export class Perfil implements OnInit {
  private authService = inject(AuthService);
  private cdr = inject(ChangeDetectorRef);
  usuario: UsuarioOut | null = null;

  ngOnInit(): void {
    this.authService.obtenerPerfil().subscribe({
      next: (u) => {
        this.usuario = u;
        this.cdr.detectChanges();
      }
    });
  }
}