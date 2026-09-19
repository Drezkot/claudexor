import Foundation
import SwiftUI

enum L10n {
    private static let russianBundle: Bundle = {
        guard
            let path = Bundle.module.path(forResource: "ru", ofType: "lproj"),
            let bundle = Bundle(path: path)
        else {
            print("[L10n] ru.lproj not found in Bundle.module")
            return Bundle.module
        }

        return bundle
    }()

    static func t(_ key: String) -> String {
        russianBundle.localizedString(
            forKey: key,
            value: key,
            table: "Localizable"
        )
    }
}
