interface SelectorProps {
    options: string[];
    selectedValue: string;
    onChange: (newValue: string) => void;
}

export function Selector({ options, selectedValue, onChange }: SelectorProps) {
    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.value);
    };
    const handleOptionClick = (option: string) => {
        onChange(option);
    };

    return (
        <div data-component="Selector">
            <h2>Session</h2>
            <ul>
                {options.map((option) => {
                    const isSelected = option === selectedValue;
                    return (
                        <li
                            key={option}
                            onClick={() => handleOptionClick(option)}
                            className={isSelected ? "item-selected" : "item-default"}
                        >
                            {option}
                        </li>
                    );
                })}
            </ul>
            <input
                type="text"
                value={selectedValue}
                onChange={handleInputChange}
                placeholder="Type or select..."
            />
        </div>
    )
}