# Guia para generar APK de la App Movil

## Requisitos previos
- Tener Node.js instalado
- Tener una cuenta de Expo (https://expo.dev)
- Tener EAS CLI instalado

## Paso 1: Instalar EAS CLI
```bash
npm install -g eas-cli
```

## Paso 2: Iniciar sesion en Expo
```bash
eas login
```
Si no tienes cuenta, creala gratis en https://expo.dev/signup

## Paso 3: Configurar el proyecto
Dentro de la carpeta `mobile-app`:
```bash
cd mobile-app
eas build:configure
```
Esto crea el archivo `eas.json`.

## Paso 4: Editar eas.json
Reemplaza el contenido de `eas.json` con:
```json
{
  "cli": {
    "version": ">= 3.0.0"
  },
  "build": {
    "preview": {
      "distribution": "internal",
      "android": {
        "buildType": "apk"
      }
    },
    "production": {
      "android": {
        "buildType": "app-bundle"
      }
    }
  }
}
```

## Paso 5: Build del APK
```bash
eas build -p android --profile preview
```

Expo Compilara tu app en la nube y te dara un link para descargar el APK.

## Paso 6: Descargar el APK
- Entra al link que te dio el comando anterior
- Haz clic en "Download"
- Transfiere el APK a tu celular
- Instala (activa "Fuentes desconocidas" en ajustes)

## Paso 7: Configurar la API
Antes de hacer build, edita `mobile-app/config.js`:
```js
export const API_BASE_URL = 'https://TU-SERVICE.run.app';
```

## Notas
- El APK funciona sin Expo Go
- Para iOS necesitas una cuenta de Apple Developer ($99/anio)
- Cada vez que cambies algo, vuelve a ejecutar `eas build`
