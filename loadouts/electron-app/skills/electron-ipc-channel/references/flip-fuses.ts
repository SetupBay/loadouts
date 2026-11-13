// Run after packaging and before code signing, e.g. from an electron-builder afterPack hook
// or an Electron Forge packageAfterCopy hook. Pass the path to the packaged Electron binary.
import { flipFuses, FuseV1Options, FuseVersion } from "@electron/fuses";

export async function hardenBinary(electronBinary: string, macArm64: boolean): Promise<void> {
  await flipFuses(electronBinary, {
    version: FuseVersion.V1,
    resetAdHocDarwinSignature: macArm64,
    [FuseV1Options.RunAsNode]: false,
    [FuseV1Options.EnableCookieEncryption]: true,
    [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
    [FuseV1Options.EnableNodeCliInspectArguments]: false,
    [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
    [FuseV1Options.OnlyLoadAppFromAsar]: true,
    [FuseV1Options.GrantFileProtocolExtraPrivileges]: false,
  });
}
