import { Component, OnInit, inject, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { OrdersService, Order } from '../../../core/services/orders.service';
import { PaymentService } from '../../../core/services/payment.service';
import { UiService } from '../../../core/services/ui.service';

@Component({
  selector: 'app-my-orders',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './my-orders.html',
  styleUrl: './my-orders.scss',
})
export class MyOrdersComponent implements OnInit {
  private ordersService = inject(OrdersService);
  private paymentService = inject(PaymentService);
  private router = inject(Router);
  private ui = inject(UiService);
  private cdr = inject(ChangeDetectorRef);

  payingOrderId: number | null = null;

  orders: Order[] = [];
  loading = true;

  ngOnInit(): void {
    this.loading = true;
    this.ordersService.getBuyerOrders().subscribe({
      next: (data) => {
        this.orders = data;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.loading = false;
        this.cdr.markForCheck();
      },
    });
  }

  statusClass(status: string): string {
    const map: Record<string, string> = {
      pending: 'bg-amber-100 text-amber-800',
      accepted: 'bg-blue-100 text-blue-800',
      rejected: 'bg-red-100 text-red-800',
      shipped: 'bg-indigo-100 text-indigo-800',
      delivered: 'bg-emerald-100 text-emerald-800',
      cancelled: 'bg-gray-100 text-gray-700',
    };
    return map[status] ?? 'bg-gray-100 text-gray-700';
  }

  payOrder(order: Order): void {
    this.payingOrderId = order.id;
    this.paymentService.createIntent(order.id).subscribe({
      next: (payment) => {
        this.payingOrderId = null;
        this.cdr.markForCheck();
        if (payment.checkout_url) {
          this.paymentService.startPayment(payment);
          return;
        }
        this.router.navigate(['/payment/mock'], {
          queryParams: { payment_id: payment.id, client_secret: payment.client_secret },
        });
      },
      error: (err) => {
        this.payingOrderId = null;
        this.cdr.markForCheck();
        this.ui.showInfo(err.error?.message || 'Could not start payment.');
      },
    });
  }
}
