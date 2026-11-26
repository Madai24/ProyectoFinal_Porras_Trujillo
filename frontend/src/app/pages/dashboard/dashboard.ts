import { Component, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ReportesService } from '../../services/reportes';
import { CatalogosService } from '../../services/catalogos';
import { Catalogo, EstadisticasOut, ReporteOut } from '../../models/huellas.models';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  private reportesService = inject(ReportesService);
  private catalogosService = inject(CatalogosService);

  reportes: ReporteOut[] = [];
  estadisticas: EstadisticasOut | null = null;
  distritos: Catalogo[] = [];
  estados: Catalogo[] = [];

  filtroDistrito?: number;
  filtroEstado?: number;
  cargando = true;
  apiUrl = 'http://127.0.0.1:8000';

  ngOnInit(): void {
    this.cargarCatalogos();
    this.cargarEstadisticas();
    this.cargarReportes();
  }

  cargarCatalogos() {
    this.catalogosService.getDistritos().subscribe(data => this.distritos = data);
    this.catalogosService.getEstados().subscribe(data => this.estados = data);
  }

  cargarEstadisticas() {
    this.reportesService.obtenerEstadisticas().subscribe(data => this.estadisticas = data);
  }

  cargarReportes() {
    this.cargando = true;
    this.reportesService.listar(this.filtroDistrito, this.filtroEstado).subscribe({
      next: (data) => {
        this.reportes = data;
        this.cargando = false;
      },
      error: () => this.cargando = false
    });
  }

  limpiarFiltros() {
    this.filtroDistrito = undefined;
    this.filtroEstado = undefined;
    this.cargarReportes();
  }

  obtenerUrlImagen(url: string): string {
    if (!url) return '';
    return url.startsWith('http') ? url : `${this.apiUrl}${url.startsWith('/') ? '' : '/'}${url}`;
  }
}