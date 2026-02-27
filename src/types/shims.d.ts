declare module "pdf-to-printer" {
  export interface Printer {
    name: string;
  }

  export interface PrintOptions {
    printer?: string;
  }

  export function getPrinters(): Promise<Printer[]>;
  export function print(file: string, options?: PrintOptions): Promise<void>;
}

