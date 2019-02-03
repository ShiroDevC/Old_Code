using Microsoft.Xna.Framework.Content;

namespace pirates.GameObjects
{
    /// <summary>
    ///  Interface for all Classes of real Game Objects that will be rendered.
    /// </summary>
    interface IGameObject
    {
        /// <summary>
        ///  Initialize method for all GameObjects.
        /// </summary>
        // ReSharper disable once UnusedMemberInSuper.Global
        void Initialize();

        /// <summary>
        /// Load assets.
        /// </summary>
        /// <param name="content"></param>
        // ReSharper disable once UnusedMemberInSuper.Global
        void LoadContent(ContentManager content);
        

    }
}
