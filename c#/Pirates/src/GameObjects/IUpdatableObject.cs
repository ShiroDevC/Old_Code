using Microsoft.Xna.Framework;

namespace pirates.GameObjects
{
    /// <summary>
    ///  For all Objects that should have an update method.
    /// </summary>
    interface IUpdatableObject
    {
        /// <summary>
        ///  Upatemethod for all objects that need to be updated on runtime.
        /// </summary>
        // ReSharper disable once UnusedMember.Global
        // ReSharper disable once UnusedParameter.Global
        // ReSharper disable once UnusedMemberInSuper.Global
        void Update(GameTime gameTime);
        
    }
}
