// Example Edit Mode test. Copy to Assets/Tests/EditMode/HealthTests.cs next to the test .asmdef.
// Tests plain C# logic (no scene, no frames), so it runs in milliseconds from the command line.
using NUnit.Framework;

namespace Game.Tests
{
    public class HealthTests
    {
        [Test]
        public void Damage_ReducesHealth_AndNeverGoesBelowZero()
        {
            var health = new Health(max: 10);
            health.TakeDamage(4);
            Assert.That(health.Current, Is.EqualTo(6));
            health.TakeDamage(50);
            Assert.That(health.Current, Is.EqualTo(0));
            Assert.That(health.IsDead, Is.True);
        }

        [TestCase(0)]
        [TestCase(-3)]
        public void Damage_IgnoresZeroOrNegative(int amount)
        {
            var health = new Health(max: 10);
            health.TakeDamage(amount);
            Assert.That(health.Current, Is.EqualTo(10));
        }
    }
}
