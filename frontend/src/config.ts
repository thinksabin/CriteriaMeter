// Compile-time constants injected from config.yml via vite.config.ts define block.
// To change these values, edit config.yml at the project root and restart the dev server.
declare const __APP_NAME__: string
declare const __APP_VERSION__: string

export const APP_NAME: string    = __APP_NAME__
export const APP_VERSION: string = __APP_VERSION__
