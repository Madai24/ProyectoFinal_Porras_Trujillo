import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { ReportesService } from '../../services/reportes';
import { CatalogosService } from '../../services/catalogos';
import { AuthService } from '../../services/auth';
import { Catalogo, ReporteOut, UsuarioOut } from '../../models/huellas.models';

@Component({
  selector: 'app-detalle-reporte',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './detalle-reporte.html',
  styleUrl: './detalle-reporte.css'
})
export class DetalleReporte implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private reportesService = inject(ReportesService);
  private catalogosService = inject(CatalogosService);
  private cdr = inject(ChangeDetectorRef);
  authService = inject(AuthService);

  reporte: ReporteOut | null = null;
  usuario: UsuarioOut | null = null;
  estados: Catalogo[] = [];
  nuevoEstadoId?: number;
  apiUrl = 'http://127.0.0.1:8000';

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    if (id) {
      this.reportesService.obtenerPorId(id).subscribe({
        next: (rep) => {
          this.reporte = rep;
          this.nuevoEstadoId = rep.estado.id;
          this.cdr.detectChanges();
        },
        error: () => {
          this.router.navigate(['/']);
        }
      });
    }

    this.catalogosService.getEstados().subscribe(e => {
      this.estados = e;
      this.cdr.detectChanges();
    });

    if (this.authService.estaAutenticado()) {
      this.authService.obtenerPerfil().subscribe({
        next: (u) => {
          this.usuario = u;
          this.cdr.detectChanges();
        },
        error: () => {}
      });
    }
  }

  obtenerUrlImagen(url: string): string {
    if (!url) return '';
    return url.startsWith('http') ? url : `${this.apiUrl}${url.startsWith('/') ? '' : '/'}${url}`;
  }

  cambiarEstado() {
    if (!this.reporte || !this.nuevoEstadoId) return;
    this.reportesService.actualizarEstado(this.reporte.id, this.nuevoEstadoId).subscribe({
      next: (actualizado) => {
        this.reporte = actualizado;
        this.cdr.detectChanges();
        alert('Estado actualizado.');
      },
      error: (err) => alert(err.error?.detail || 'No tienes permisos para cambiar el estado.')
    });
  }

  eliminarReporte() {
    if (!this.reporte || !confirm('¿Seguro que deseas eliminar este reporte?')) return;
    this.reportesService.eliminar(this.reporte.id).subscribe({
      next: () => {
        alert('Reporte eliminado.');
        this.router.navigate(['/']);
      },
      error: (err) => alert(err.error?.detail || 'No tienes permisos para eliminar este reporte.')
    });
  }
}