import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'highlight',
  standalone: true
})
export class HighlightPipe implements PipeTransform {
  transform(text: string, query: string): string {
    if (!query) return text;
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escaped, 'gi');
    return text.replace(regex, match => `<mark class="bg-indigo-100 text-indigo-600 rounded px-0.5">${match}</mark>`);
  }
}
