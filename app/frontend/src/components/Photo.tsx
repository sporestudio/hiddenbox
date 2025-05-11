"use client";

interface PhotoProps {
  imageSrc: string;
  darkImageSrc: string;
  imageAlt: string;
}

export default function Photo({ imageSrc, darkImageSrc, imageAlt }: PhotoProps) {
    return (
        <div className="relative flex items-center justify-center">
            <div className="relative h-[150px] w-[150px] xl:h-[253px] xl:w-[253px]">
            {/* Image light theme */}
            <img 
                src={imageSrc} 
                alt={imageAlt}
                className="h-full w-full object-contain dark:hidden"
            />
            {/* Image dark theme */}
            <img 
                src={darkImageSrc} 
                alt={imageAlt}
                className="h-full w-full object-contain hidden dark:block"
            />
            </div>
        </div>
    );
}