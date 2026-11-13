// Example Phaser 4 scene: assets in preload, pooled bullets, delta-based movement, keyboard and pointer input,
// constants in one place and listeners removed on shutdown.
import Phaser from "phaser";

export const TUNING = {
  playerSpeed: 300, // pixels per second
  bulletSpeed: 600,
  fireCooldownMs: 200,
  maxBullets: 30,
} as const;

export class GameScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private bullets!: Phaser.Physics.Arcade.Group;
  private cursors?: Phaser.Types.Input.Keyboard.CursorKeys;
  private lastFired = 0;

  constructor() {
    super("Game");
  }

  preload(): void {
    this.load.image("player", "assets/player.png");
    this.load.image("bullet", "assets/bullet.png");
  }

  create(): void {
    const { width, height } = this.scale;
    this.player = this.physics.add.sprite(width / 2, height - 60, "player");
    this.player.setCollideWorldBounds(true);

    this.bullets = this.physics.add.group({ defaultKey: "bullet", maxSize: TUNING.maxBullets });
    this.cursors = this.input.keyboard?.createCursorKeys();

    this.input.on(Phaser.Input.Events.POINTER_DOWN, this.fire, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.input.off(Phaser.Input.Events.POINTER_DOWN, this.fire, this);
    });
  }

  update(time: number, delta: number): void {
    const dx = (this.cursors?.left.isDown ? -1 : 0) + (this.cursors?.right.isDown ? 1 : 0);
    this.player.x += dx * TUNING.playerSpeed * (delta / 1000);

    if (this.cursors?.space.isDown && time > this.lastFired + TUNING.fireCooldownMs) {
      this.fire();
      this.lastFired = time;
    }

    // Return off-screen bullets to the pool instead of destroying them.
    for (const child of this.bullets.getChildren()) {
      const b = child as Phaser.Physics.Arcade.Image;
      if (b.active && b.y < -20) this.bullets.killAndHide(b);
    }
  }

  private fire(): void {
    const b = this.bullets.get(this.player.x, this.player.y - 20) as Phaser.Physics.Arcade.Image | null;
    if (!b) return; // pool exhausted: skip this shot rather than allocate
    b.setActive(true).setVisible(true);
    b.enableBody(true, this.player.x, this.player.y - 20, true, true);
    b.setVelocityY(-TUNING.bulletSpeed);
  }
}
