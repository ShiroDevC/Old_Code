using Microsoft.Xna.Framework;
using pirates.AI.Pathfinding;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Interface for all GameObjects, that are able to battle.
    /// </summary>
    public interface IBattleObject
    {
        /// <summary>
        ///  Initializes the attack of the ship. Sets the Path for the ship and 
        ///  sets up the tracking of the enemy Ships position. Computes where the 
        ///  ship will start shooting.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        // ReSharper disable once UnusedParameter.Global
        void Attack(AShip targetShip);

        /// <summary>
        ///  Initializes the defending Mode of the ship. Sets the Path to the position
        ///  to defend. Activates tracking of enemy ships in range.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        // ReSharper disable once UnusedParameter.Global
        void Defend(Path target);

        /// <summary>
        ///  Update method to implement battle behaviour of the IBattleObjects.
        /// </summary>
        void Update(GameTime gameTime);

        /// <summary>
        ///  The ship to be attacked.
        /// </summary>
        // ReSharper disable once UnusedMemberInSuper.Global
        AShip TargetShip { get; set; }

        bool Chasing { get; }


    }
}
