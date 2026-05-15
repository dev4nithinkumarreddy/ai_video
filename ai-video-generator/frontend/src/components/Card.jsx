import React from 'react';
import { motion } from 'framer-motion';

const Card = ({ children, className = '', hover = true }) => {
  return (
    <motion.div
      whileHover={{ scale: hover ? 1.02 : 1 }}
      transition={{ duration: 0.2 }}
      className={`
        bg-white rounded-lg shadow-lg overflow-hidden
        ${hover ? 'shadow-xl' : ''}
        ${className}
      `.trim()}
    >
      {children}
    </motion.div>
  );
};

export default Card;
